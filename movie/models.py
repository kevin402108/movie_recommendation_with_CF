from django.db import models
from django.db.models import Avg
from django.core import validators
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

class Genre(models.Model):
    name = models.CharField(max_length=100,verbose_name="电影类别")

    class Meta:
        db_table = 'Genre'
        verbose_name = "电影类别"
        verbose_name_plural = "电影类别"

    def __str__(self):
        return f"{self.name}"

class Movie(models.Model):
    # 电影名
    name = models.CharField(max_length=256, verbose_name="电影名")
    # imdb_id是info文件里面的电影顺序
    imdb_id = models.IntegerField(verbose_name="IMDb编号")
    # 时长
    time = models.CharField(max_length=256, blank=True, verbose_name="电影时长")
    # 类型
    genre = models.ManyToManyField(Genre, verbose_name="电影类型")
    # 发行时间
    release_time = models.CharField(max_length=256, blank=True, verbose_name="发行时间")
    # 简介
    intro = models.TextField(blank=True, verbose_name="电影简介")
    # 导演
    director = models.CharField(max_length=256, blank=True, verbose_name="导演")
    # 编剧
    writers = models.CharField(max_length=256, blank=True, verbose_name="编剧")
    # 演员
    actors = models.CharField(max_length=512, blank=True, verbose_name="演员")
    # 电影和电影之间的相似度,A和B的相似度与B和A的相似度是一致的，所以symmetrical设置为True
    movie_similarity=models.ManyToManyField("self",through="Movie_similarity",symmetrical=False)

    class Meta:
        db_table = 'Movie'
        verbose_name = "电影"
        verbose_name_plural = "电影"

    def __str__(self):
        return f"{self.name}"

    def get_score(self):
        # 定义一个获取平均分的方法，模板中直接调用即可
        # 格式 {'score__avg': 3.125}
        result_dct = self.movie_rating_set.aggregate(Avg('score'))
        try:
            # 只保留一位小数
            result = round(result_dct['score__avg'], 1)
        except TypeError:
            return 0
        else:
            return result

    def get_user_score(self, user):
        return self.movie_rating_set.filter(user=user).values('score')

    def get_score_int_range(self):
        return range(int(self.get_score()))

    def get_genre(self):
        genre_dct = self.genre.all().values('name')
        genre_lst = []
        for dct in genre_dct.values():
            genre_lst.append(dct['name'])
        return genre_lst

    def get_similarity(self,k=5):
        # 获取5部最相似的电影的id
        similarity_movies=self.movie_similarity.all()[:k]
        print(similarity_movies)
        # movies=Movie.objects.filter(=similarity_movies)
        # print(movies)
        return similarity_movies

class Movie_similarity(models.Model):
    movie_source=models.ForeignKey(Movie,related_name='movie_source',on_delete=models.CASCADE,verbose_name="源电影")
    movie_target=models.ForeignKey(Movie,related_name='movie_target',on_delete=models.CASCADE,verbose_name="目标电影")
    similarity=models.FloatField(verbose_name="相似度")
    class Meta:
        # 按照相似度降序排序
        ordering=['-similarity']
        verbose_name = "电影相似度"
        verbose_name_plural = "电影相似度"

class User(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=256, verbose_name="密码")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    rating_movies = models.ManyToManyField(Movie, through="Movie_rating")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'User'
        verbose_name = "用户"
        verbose_name_plural = "用户"


class Movie_rating(models.Model):
    # 评分的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    # 评分的电影
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False)
    # 分数
    score = models.FloatField(verbose_name="评分")
    # 评论，可选
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'Movie_rating'
        verbose_name = "电影评分记录"
        verbose_name_plural = "电影评分记录"

class Movie_hot(models.Model):
    '''存放最热门的一百部电影'''
    # 电影外键
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE,verbose_name="电影名")
    # 评分人数
    rating_number=models.IntegerField(verbose_name="评分人数")
    class Meta:
        db_table='Movie_hot'
        ordering=['-rating_number']
        verbose_name = "热门电影"
        verbose_name_plural = "热门电影"
    def __str__(self):
        return f"<Movie_hot:{self.movie.name},{self.rating_number}>"



@receiver(m2m_changed, sender=Movie.genre.through)
def auto_calculate_similarity_on_genre_change(sender, instance, action, **kwargs):
    print(f"m2m_changed信号触发：电影 {instance.name}, action={action}")
    # 当genre关系被添加完成后触发
    if action == 'post_add':
        print(f"开始计算相似度 for {instance.id}")
        calculate_new_movie_similarity(instance.id)


def calculate_new_movie_similarity(new_movie_id):
    """
    新增电影时，计算它与同一类别电影的相似度并写入相似度表
    :param new_movie_id: 新添加的电影ID
    :return: 成功写入的相似度记录数
    """
    try:
        # 1. 获取新电影对象
        new_movie = Movie.objects.get(id=new_movie_id)
        print(f"开始计算新电影「{new_movie.name}」的相似度...")

        # 2. 筛选同一类别下的其他电影
        # 获取新电影的所有类别
        genres = new_movie.genre.all()
        print(f"新电影「{new_movie.name}」的类别：{genres}")
        if not genres:
            print("该电影未关联任何类别，无法计算同类别相似度")
            return 0

        # 找到同一类别、排除自身的电影
        same_genre_movies = Movie.objects.filter(
            genre__in=genres
        ).exclude(id=new_movie_id).distinct()

        if not same_genre_movies:
            print("同一类别下无其他电影，无需计算")
            return 0

        # 3. 提取电影的内容特征（导演、编剧、演员、类别）
        def extract_features(movie):
            features = set()  # 用集合去重
            # 导演（单个值）
            if movie.director:
                features.add(movie.director.strip())
            # 编剧（按|拆分多个值）
            if movie.writers:
                for writer in movie.writers.split("|"):
                    writer_clean = writer.strip()
                    if writer_clean:
                        features.add(writer_clean)
            # 演员（按|拆分多个值）
            if movie.actors:
                for actor in movie.actors.split("|"):
                    actor_clean = actor.strip()
                    if actor_clean:
                        features.add(actor_clean)
            # 类别名称
            for genre in movie.genre.all():
                genre_clean = genre.name.strip()
                if genre_clean:
                    features.add(genre_clean)
            return features

        # 提取新电影的特征集合
        new_movie_features = extract_features(new_movie)
        if not new_movie_features:
            print("新电影无有效特征，无法计算相似度")
            return 0

        # 4. 遍历同类别电影，计算相似度并写入表
        created_count = 0
        for other_movie in same_genre_movies:
            # 提取其他电影的特征
            other_movie_features = extract_features(other_movie)
            if not other_movie_features:
                continue  # 无特征的电影跳过

            # 计算杰卡德相似度：(交集大小) / (并集大小)
            intersection = len(new_movie_features & other_movie_features)
            union = len(new_movie_features | other_movie_features)
            similarity = round(intersection / union, 12) if union != 0 else 0.0

            # 避免重复记录（只存 new_movie → other_movie 的方向）
            if Movie_similarity.objects.filter(
                    movie_source_id=new_movie.id,
                    movie_target_id=other_movie.id
            ).exists():
                print(f"已存在「{new_movie.id}→{other_movie.id}」的记录，跳过")
                continue

            if similarity < 0.25:
                continue

            # 写入相似度表
            Movie_similarity.objects.create(
                similarity=similarity,
                movie_source_id=new_movie.id,
                movie_target_id=other_movie.id
            )
            created_count += 1
            print(f"「{new_movie.name}」与「{other_movie.name}」的相似度：{similarity}")

        print(f"计算完成，共写入 {created_count} 条相似度记录")
        return created_count

    except Movie.DoesNotExist:
        print(f"电影ID {new_movie_id} 不存在")
        return 0
    except Exception as e:
        print(f"计算失败：{str(e)}")
        return 0