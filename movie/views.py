import csv
import time
import os.path
from math import sqrt
from django.contrib import messages
from django.db.models import Avg, Count, Max
from django.http import HttpResponse, request
from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm, LoginForm, CommentForm
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Movie, Genre, Movie_rating, Movie_similarity, Movie_hot
import redis
import json

# DO NOT MAKE ANY CHANGES
BASE = os.path.dirname(os.path.abspath(__file__))

'''所有注释掉的函数，如果数据库没有出错，不要执行，并且应该在urls中注释掉相应的路径，以免误入'''

'''!!! 导入csv文件用'''
# def get_genre():
#     '''导入所有电影类型'''
#     path=os.path.join(BASE,'static\movie\info\genre.txt')
#     with open(path) as fb:
#         for line in fb:
#             Genre.objects.create(name=line.strip())
#
# def get_movie_info():
#     '''导入所有电影信息，设置它们的类型'''
#     path=os.path.join(BASE,'static\movie\info\info.csv')
#     with open(path) as fb:
#         reader=csv.reader(fb)
#         title=reader.__next__()
#         # 读取title信息 id,name,url,time,genre,release_time,intro,directores,writers,starts
#         # 这里的id是imbd的id，根据它来访问static文件夹下面的poster
#         title_dct=dict(zip(title,range(len(title))))
#         # print(title_dct)
#         # print(path)
#         for i,line in enumerate(reader):
#             m=Movie.objects.create(name=line[title_dct['name']],
#                                  imdb_id=line[title_dct['id']],
#                                  time=line[title_dct['time']],
#                                  release_time=line[title_dct['release_time']],
#                                  intro=line[title_dct['intro']],
#                                  director=line[title_dct['directors']],
#                                  writers=line[title_dct['writers']],
#                                  actors=line[title_dct['starts']])
#             # 必须要先保存才能建立关系
#             m.save()
#             # 建立类型关系
#             for genre in line[title_dct['genre']].split('|'):
#                 # 找到类型 genre_object
#                 go=Genre.objects.filter(name=genre).first()
#                 # print(go)
#                 m.genre.add(go)
#             if i%1000==0:
#                 print(i)    # 控制台查看进度用
#             # pass
#
# def get_user_and_rating():
#     '''
#     获取ratings文件，设置用户信息和对电影的评分
#     由于用户没有独立的信息，默认用这种方式保存用户User: name=userId,password=userId,email=userId@1.com
#     通过imdb_id对电影进行关联，设置用户对电影的评分,comment默认为空
#     '''
#     path = os.path.join(BASE, r'static\movie\info\ratings.csv')
#     with open(path) as fb:
#         reader=csv.reader(fb)
#         # userId,movieId,rating,timestamp,timestamp不用管
#         title=reader.__next__()
#         title_dct=dict(zip(title,range(len(title))))
#         # csv文件中，一条记录就是一个用户对一部电影的评分和时间戳，一个用户可能有多条评论
#         # 所以要先取出用户所有的评分，设置成一个字典,格式为{ user:{movie1:rating, movie2:rating, ...}, ...}
#         user_id_dct=dict()
#         for line in reader:
#             user_id=line[title_dct['userId']]
#             imdb_id=line[title_dct['movieId']]
#             rating=line[title_dct['rating']]
#             user_id_dct.setdefault(user_id,dict())
#             user_id_dct[user_id][imdb_id]=rating
#     # 对所有用户和评分记录
#     for user_id,ratings in user_id_dct.items():
#         u=User.objects.create(name=user_id,password=user_id,email=f'{user_id}@1.com')
#         # 必须先保存
#         u.save()
#         # 开始加入评分记录
#         for imdb_id,rating in ratings.items():
#             # Movie_rating(uid=)
#             movie=Movie.objects.get(imdb_id=imdb_id)
#             relation=Movie_rating(user=u,movie=movie,score=rating,comment='')
#             relation.save()
#             # break
#         print(f'{user_id} process success')
#         # break
#
# def index(request):
#     # 临时的index函数，用来导入数据库
#     # get_genre()
#     # get_movie_info()
#     # get_user_rating()
#     context={'movie':Movie.objects.filter(name="Toy Story (1995) ").first()}
#     # print(Movie.objects.filter(name="Toy Story (1995) ").first())
#     return render(request, 'movie/index.html',context=context)
'''!!! 导入csv文件用'''

'''!!! 恢复评分信息用，如果movie_rating表没有出错，不需要执行下面的函数'''
# def get_ratings():
#     '''这个函数是用来恢复movie_rating表的
#         之前不小心update了所有记录，导致数据库表全部更新成一条了，也就是10万条一样的评分
#         现在要重新导入
#     '''
#     '''
#     获取ratings文件，设置用户信息和对电影的评分
#     由于用户没有独立的信息，默认用这种方式保存用户User: name=userId,password=userId,email=userId@1.com
#     通过imdb_id对电影进行关联，设置用户对电影的评分,comment默认为空
#     '''
#     path = os.path.join(BASE, r'static\movie\info\ratings.csv')
#     with open(path) as fb:
#         reader=csv.reader(fb)
#         # userId,movieId,rating,timestamp,timestamp不用管
#         title=reader.__next__()
#         title_dct=dict(zip(title,range(len(title))))
#         # csv文件中，一条记录就是一个用户对一部电影的评分和时间戳，一个用户可能有多条评论
#         # 所以要先取出用户所有的评分，设置成一个字典,格式为{ user:{movie1:rating, movie2:rating, ...}, ...}
#         user_id_dct=dict()
#         for line in reader:
#             user_id=line[title_dct['userId']]
#             imdb_id=line[title_dct['movieId']]
#             rating=line[title_dct['rating']]
#             user_id_dct.setdefault(user_id,dict())
#             user_id_dct[user_id][imdb_id]=rating
#     # 对所有用户和评分记录
#     for user_id,ratings in user_id_dct.items():
#         # 获取用户
#         u=User.objects.get(name=user_id)
#
#         # 开始加入评分记录
#         for imdb_id,rating in ratings.items():
#             # Movie_rating(uid=)
#             movie=Movie.objects.get(imdb_id=imdb_id)
#             relation=Movie_rating(user=u,movie=movie,score=rating,comment='')
#             relation.save()
#             # break
#         print(f'{user_id} process success')
'''!!! 恢复评分信息用'''

'''!!! 修复数据库用'''
# def fixdb(request):
#     # 修复数据库用
#     # !!!
#     # get_ratings()
#     # !!!
#     print("fix db success")
#     return redirect((reverse('movie:index')))
'''!!! 修复数据库用'''

'''!!! 导入电影相似度用'''

# def calc_movie_similarity(request):
#     path = os.path.join(BASE, r'static\movie\info\movie_similarity.csv')
#     with open(path) as fb:
#         reader=csv.reader(fb)
#         reader.__next__()
#         for line in reader:
#             # 把它们都转换成值
#             line=list(map(eval,line))
#             m1,m2,val=line
#             movie1=Movie.objects.get(imdb_id=m1)
#             movie2=Movie.objects.get(imdb_id=m2)
#             # print(movie1,movie2)
#             # 保存记录到数据库中,因为csv表中存储了每部电影的十条记录，我们保存就行了
#             record=Movie_similarity(movie_source=movie1,movie_target=movie2,similarity=val)
#             record.save()
#
#     print("写入相似度成功")
#     return redirect((reverse('movie:index')))


'''!!! 导入电影相似度用'''


class IndexView(ListView):
    model = Movie
    template_name = 'movie/index.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'imdb_id'
    page_kwarg = 'p'

    def get_queryset(self):
        # 返回前1000部电影
        return Movie.objects.filter(imdb_id__lte=1000)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IndexView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        # print(context)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


class PopularMovieView(ListView):
    model = Movie_hot
    template_name = 'movie/hot.html'
    paginate_by = 15
    context_object_name = 'movies'
    # ordering = '-movie_hot__rating_number' # 没有效果
    page_kwarg = 'p'

    def get_queryset(self):
        # 初始化 计算评分人数最多的100部电影，并保存到数据库中
        # ######################
        # movies = Movie.objects.annotate(nums=Count('movie_rating__score')).order_by('-nums')[:100]
        # print(movies)
        # print(movies.values("nums"))
        # for movie in movies:
            # print(movie,movie.nums)
            # record = Movie_hot(movie=movie, rating_number=movie.nums)
            # record.save()
        # ######################

        hot_movies=Movie_hot.objects.all().values("movie_id")
        # print(hot_movies)
        # for movie in hot_movies:
            # print(movie)
            # print(movie.imdb_id,movie.rating_number)
        # Movie.objects.filter(movie_hot__rating_number=)
        # 一个bug!这里filter出来虽然是正确的100部电影，但是会按照imdb_id排序，导致正确的结果被破坏了！也就是得不到100部热门电影的正确顺序！
        # movies=Movie.objects.filter(id__in=hot_movies.values("imdb_id"))
        # 找出100部热门电影，同时按照评分人数排序
        # 因此我们必须要手动排序一次。另外也不太好用
        movies=Movie.objects.filter(id__in=hot_movies).annotate(nums=Max('movie_hot__rating_number')).order_by('-nums')
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PopularMovieView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        # print(context)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


class TagView(ListView):
    model = Movie
    template_name = 'movie/tag.html'
    paginate_by = 15
    context_object_name = 'movies'
    # ordering = 'movie_rating__score'
    page_kwarg = 'p'

    def get_queryset(self):
        if 'genre' not in self.request.GET.dict().keys():
            movies = Movie.objects.all()
            return movies[100:200]
        else:
            movies = Movie.objects.filter(genre__name=self.request.GET.dict()['genre'])
            print(movies)
            return movies[:100]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagView, self).get_context_data(*kwargs)
        if 'genre' in self.request.GET.dict().keys():
            genre = self.request.GET.dict()['genre']
            context.update({'genre': genre})
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


class SearchView(ListView):
    model = Movie
    template_name = 'movie/search.html'
    paginate_by = 15
    context_object_name = 'movies'
    # ordering = 'movie_rating__score'
    page_kwarg = 'p'

    def get_queryset(self):
        movies = Movie.objects.filter(name__icontains=self.request.GET.dict()['keyword'])
        print(movies)
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        # self.genre=self.request.GET.dict()['genre']
        context = super(SearchView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        context.update({'keyword': self.request.GET.dict()['keyword']})
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# 注册视图
class RegisterView(View):
    def get(self, request):
        return render(request, 'movie/register.html')

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 没毛病，保存
            form.save()
            return redirect(reverse('movie:index'))
        else:
            # 表单验证失败，重定向到注册页面
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            print(form.errors.get_json_data())
            return redirect(reverse('movie:register'))


# 登录视图
class LoginView(View):
    def get(self, request):
        return render(request, 'movie/login.html')

    def post(self, request):
        print(request.POST)
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            pwd = form.cleaned_data.get('password')
            user = User.objects.filter(name=name, password=pwd).first()
            # username = form.cleaned_data.get('name')
            # print(username)
            # pwd = form.cleaned_data.get('password')
            if user:
                # 登录成功，在session 里面加上当前用户的id，作为标识
                request.session['user_id'] = user.id
                return redirect(reverse('movie:index'))
                if remember:
                    # 设置为None，则表示使用全局的过期时间
                    request.session.set_expiry(None)
                else:
                    request.session.set_expiry(0)
            else:
                print('用户名或者密码错误')
                # messages.add_message(request,messages.INFO,'用户名或者密码错误!')
                messages.info(request, '用户名或者密码错误!')
                return redirect(reverse('movie:login'))
        else:
            print("error!!!!!!!!!!!")
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            print(form.errors.get_json_data())
            return redirect(reverse('movie:login'))


def UserLogout(request):
    # 登出，立即停止会话
    request.session.set_expiry(-1)
    return redirect(reverse('movie:index'))


class MovieDetailView(DetailView):
    '''电影详情页面'''
    model = Movie
    template_name = 'movie/detail.html'
    # 上下文对象的名称
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        # 重写获取上下文方法，增加评分参数
        context = super().get_context_data(**kwargs)
        # 判断是否登录用
        login = True
        try:
            user_id = self.request.session['user_id']
        except KeyError as e:
            login = False  # 未登录

        # 获得电影的pk
        pk = self.kwargs['pk']
        movie = Movie.objects.get(pk=pk)

        if login:
            # 已经登录，获取当前用户的历史评分数据
            user = User.objects.get(pk=user_id)

            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            # 默认值
            score = 0
            comment = ''
            if rating:
                score = rating.score
                comment = rating.comment
            context.update({'score': score, 'comment': comment})

        similarity_movies = movie.get_similarity()
        # 获取与当前电影最相似的电影
        context.update({'similarity_movies': similarity_movies})
        # 判断是否登录，没有登录则不显示评分页面
        context.update({'login': login})

        return context

    # 接受评分表单,pk是当前电影的数据库主键id
    def post(self, request, pk):
        url = request.get_full_path()
        form = CommentForm(request.POST)
        if form.is_valid():
            # 获取分数和评论
            score = form.cleaned_data.get('score')
            comment = form.cleaned_data.get('comment')
            print(score, comment)
            # 获取用户和电影
            user_id = request.session['user_id']
            user = User.objects.get(pk=user_id)
            movie = Movie.objects.get(pk=pk)

            # 更新一条记录
            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            if rating:
                # 如果存在则更新
                # print(rating)
                rating.score = score
                rating.comment = comment
                rating.save()
                # messages.info(request,"更新评分成功！")
            else:
                print('记录不存在')
                # 如果不存在则添加
                rating = Movie_rating(user=user, movie=movie, score=score, comment=comment)
                rating.save()
            messages.info(request, "评论成功!")

        else:
            # 表单没有验证通过
            messages.info(request, "评分不能为空!")
        return redirect(reverse('movie:detail', args=(pk,)))


class RatingHistoryView(DetailView):
    '''用户详情页面'''
    model = User
    template_name = 'movie/history.html'
    # 上下文对象的名称
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        # 这里要增加的对象：当前用户过的电影历史
        context = super().get_context_data(**kwargs)
        user_id = self.request.session['user_id']
        user = User.objects.get(pk=user_id)
        # 获取ratings即可
        ratings = Movie_rating.objects.filter(user=user)

        context.update({'ratings': ratings})
        return context


def delete_recode(request, pk):
    print(pk)
    movie = Movie.objects.get(pk=pk)
    user_id = request.session['user_id']
    print(user_id)
    user = User.objects.get(pk=user_id)
    rating = Movie_rating.objects.get(user=user, movie=movie)
    print(movie, user, rating)
    rating.delete()
    messages.info(request, f"删除 {movie.name} 评分记录成功！")
    # 跳转回评分历史
    return redirect(reverse('movie:history', args=(user_id,)))


class RecommendMovieView(ListView):  
    template_name = 'movie/recommend.html'
    model = Movie
    context_object_name = 'movies'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        # 自己实现登录检查
        if not request.session.get('user_id'):
            # 如果用户未登录，重定向到登录页面
            return redirect(reverse('movie:login'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # 从session获取用户ID，而不是从request.user
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            return Movie.objects.none()
            
        try:
            # 添加Redis连接错误处理
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()  # 检查连接是否成功
            
            # 从Redis获取推荐结果
            recommend_data = self.redis_client.get(f'recommend:{user_id}')
            
            if recommend_data:
                # 如果Redis中有推荐数据，解析并返回
                recommend_list = json.loads(recommend_data)
                movie_ids = [movie_id for movie_id, _ in recommend_list]
                return Movie.objects.filter(id__in=movie_ids)
            else:
                # 如果Redis中没有推荐数据，自动生成推荐
                print(f"Redis中没有用户 {user_id} 的推荐数据，正在生成...")
                
                # 生成推荐并存入Redis
                generate_success = generate_recommendations_for_user(user_id)
                
                if generate_success:
                    # 重新从Redis获取推荐结果
                    recommend_data = self.redis_client.get(f'recommend:{user_id}')
                    if recommend_data:
                        recommend_list = json.loads(recommend_data)
                        movie_ids = [movie_id for movie_id, _ in recommend_list]
                        return Movie.objects.filter(id__in=movie_ids)
                
                # 如果生成推荐失败，返回空列表
                return Movie.objects.none()
        except redis.RedisError as e:
            # Redis连接失败，记录错误并返回空列表
            print(f"Redis连接错误: {e}")
            return Movie.objects.none()
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RecommendMovieView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }



def generate_recommendations_for_user(user_id):
    # 配置MySQL连接
    mysql_params = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123450',
        'database': 'movie_recommend_db',
        'charset': 'utf8mb4'
    }
    
    # 从MySQL读取数据
    def read_from_mysql():
        conn = pymysql.connect(**mysql_params)
        try:
            # 读取用户评分数据
            df = pd.read_sql('SELECT user_id, movie_id, score FROM movie_rating', conn)
            return df
        finally:
            conn.close()
    
    # 实现UserCF算法，支持为单个用户生成推荐
    def user_cf_recommendation(ratings_df, target_user_id):
        # 创建用户-电影评分矩阵
        user_movie_matrix = ratings_df.pivot_table(index='user_id', columns='movie_id', values='score')
        
        # 计算用户之间的相似度（使用皮尔逊相关系数）
        user_similarity = user_movie_matrix.T.corr()
        
        # 生成推荐
        recommendations = {}
        
        if target_user_id not in user_similarity.index:
            print(f"警告：用户ID {target_user_id} 不存在于评分数据中")
            return recommendations
            
        # 获取当前用户的评分
        user_ratings = user_movie_matrix.loc[target_user_id].dropna()
        
        # 存储推荐结果
        recommendations_for_user = {}
        
        # 遍历其他用户
        for other_user_id in user_similarity.index:
            if target_user_id == other_user_id:
                continue
            
            # 获取相似度
            similarity = user_similarity.loc[target_user_id, other_user_id]
            if np.isnan(similarity):
                continue
            
            # 获取其他用户的评分
            other_ratings = user_movie_matrix.loc[other_user_id].dropna()
            
            # 找到当前用户未评分的电影
            unrated_movies = other_ratings.index.difference(user_ratings.index)
            
            # 为这些电影计算推荐分数
            for movie_id in unrated_movies:
                score = other_ratings.loc[movie_id]
                weighted_score = similarity * score
                
                if movie_id not in recommendations_for_user:
                    recommendations_for_user[movie_id] = {'total_score': 0, 'total_similarity': 0}
                
                recommendations_for_user[movie_id]['total_score'] += weighted_score
                recommendations_for_user[movie_id]['total_similarity'] += similarity
        
        # 计算最终推荐分数
        user_recommendations = []
        for movie_id, scores in recommendations_for_user.items():
            if scores['total_similarity'] > 0:
                final_score = scores['total_score'] / scores['total_similarity']
                user_recommendations.append((movie_id, final_score))
        
        # 按推荐分数降序排序
        user_recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # 保存前10个推荐
        recommendations[target_user_id] = user_recommendations[:10]
        
        return recommendations
    
    # 将推荐结果写入Redis
    def write_to_redis(recommendations, redis_host='localhost', redis_port=6379, redis_db=0):
        try:
            # 连接Redis
            redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            
            # 检查连接是否成功
            redis_client.ping()
            print(f"成功连接到Redis服务器: {redis_host}:{redis_port}")
            
            # 写入Redis
            count = 0
            for user_id, recommend_list in recommendations.items():
                # 转换为Redis存储格式：[(movie_id, score), ...]
                formatted_list = [(int(movie_id), float(score)) for movie_id, score in recommend_list]
                
                # 写入Redis，键格式为'recommend:{user_id}'
                key = f'recommend:{int(user_id)}'
                redis_client.set(key, json.dumps(formatted_list))
                
                # 验证写入是否成功
                if redis_client.exists(key):
                    count += 1
                
                print(f'User {user_id}: {formatted_list}')
            
            print(f"成功写入 {count} 条推荐数据到Redis")
            return True
        except redis.RedisError as e:
            print(f"Redis连接或写入错误: {e}")
            return False
        except Exception as e:
            print(f"其他错误: {e}")
            return False
    
    # 直接实现生成推荐的逻辑，不再嵌套定义同名函数
    try:
        # 从MySQL读取数据
        print(f'正在为用户 {user_id} 生成推荐...')
        ratings_df = read_from_mysql()
        
        # 实现UserCF推荐算法
        recommendations = user_cf_recommendation(ratings_df, user_id)
        
        if not recommendations:
            print(f"警告：没有为用户 {user_id} 生成任何推荐结果！")
            return False
        
        # 将推荐结果写入Redis
        return write_to_redis(recommendations)
    except Exception as e:
        print(f"生成推荐时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
