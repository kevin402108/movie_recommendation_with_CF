# movie/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Genre, Movie, Movie_similarity, User, Movie_rating, Movie_hot


# ==================== 内联模型配置 ====================
class MovieSimilarityInline(admin.TabularInline):
    """电影相似度内联显示"""
    model = Movie_similarity
    fk_name = 'movie_source'
    extra = 1
    verbose_name = "相似电影"
    verbose_name_plural = "相似电影管理"


class MovieRatingInline(admin.TabularInline):
    """电影评分内联显示"""
    model = Movie_rating
    extra = 1
    verbose_name = "用户评分"
    verbose_name_plural = "评分记录"


# ==================== 模型Admin类配置 ====================
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """电影类型管理"""
    list_display = ('id', 'name', 'get_movie_count')
    search_fields = ('id', 'name')
    list_per_page = 15

    def get_movie_count(self, obj):
        """获取该类型下的电影数量"""
        return obj.movie_set.count()

    get_movie_count.short_description = "电影数量"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """电影管理 - 核心配置"""
    # 列表页配置
    list_display = ('id', 'name', 'imdb_id', 'release_time', 'director',
                    'get_genre_display', 'get_avg_score', 'get_rating_count', 'get_similar_movies_count')
    list_display_links = ('name',)
    list_filter = ('release_time',)
    search_fields = ('name', 'director', 'actors', 'writers', 'intro')
    list_per_page = 20

    # 编辑页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'imdb_id', 'time', 'release_time')
        }),
        ('详情信息', {
            'fields': ('genre', 'intro', 'director', 'writers', 'actors'),
            'classes': ('collapse',)
        }),
    )

    # 内联模型
    inlines = [MovieSimilarityInline, MovieRatingInline]

    # 自定义字段显示
    def get_genre_display(self, obj):
        """显示电影类型（最多显示3个）"""
        genres = obj.genre.all()[:3]
        return ", ".join([g.name for g in genres]) if genres else "无"

    get_genre_display.short_description = "类型"

    def get_avg_score(self, obj):
        """显示平均评分"""
        score = obj.get_score()
        if score:
            # 显示星标
            stars = "★" * int(score) + "☆" * (5 - int(score))
            return f"{score:.1f} {stars}"
        return "无评分"

    get_avg_score.short_description = "评分"

    def get_rating_count(self, obj):
        """显示评分人数"""
        return obj.movie_rating_set.count()

    get_rating_count.short_description = "评分人数"

    def get_similar_movies_count(self, obj):
        """显示相似电影数量（带链接）"""
        count = obj.movie_similarity.count()
        url = reverse('admin:movie_movie_similarity_changelist') + f'?movie_source__id__exact={obj.id}'
        return format_html('<a href="{}">{} 部相似电影</a>', url, count) if count > 0 else "无"

    get_similar_movies_count.short_description = "相似电影"


@admin.register(Movie_similarity)
class MovieSimilarityAdmin(admin.ModelAdmin):
    """电影相似度管理"""
    list_display = ('id', 'get_movie_source', 'get_movie_target', 'similarity')
    list_filter = ('movie_source', 'movie_target')
    search_fields = ('movie_source__name', 'movie_target__name')
    list_per_page = 30
    ordering = ('-similarity',)

    def get_movie_source(self, obj):
        return f"{obj.movie_source.name} (ID:{obj.movie_source.imdb_id})"

    get_movie_source.short_description = "源电影"

    def get_movie_target(self, obj):
        return f"{obj.movie_target.name} (ID:{obj.movie_target.imdb_id})"

    get_movie_target.short_description = "目标电影"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """用户管理"""
    list_display = ('id', 'name', 'email', 'get_rating_count')
    list_display_links = ('name',)
    search_fields = ('name', 'email')
    list_per_page = 20

    # 字段显示顺序
    fields = ('id', 'name', 'email')

    def get_rating_count(self, obj):
        """获取用户评分数量"""
        return obj.movie_rating_set.count()

    get_rating_count.short_description = "评分数量"


@admin.register(Movie_rating)
class MovieRatingAdmin(admin.ModelAdmin):
    """电影评分管理"""
    list_display = ('id', 'get_user', 'get_movie', 'score', 'get_comment_preview')
    list_filter = ('score',)
    search_fields = ('user__name', 'movie__name', 'comment')
    list_per_page = 30

    def get_user(self, obj):
        return obj.user.name

    get_user.short_description = "用户"

    def get_movie(self, obj):
        return obj.movie.name

    get_movie.short_description = "电影"

    def get_comment_preview(self, obj):
        """评论内容预览（最多显示30字符）"""
        if obj.comment and len(obj.comment) > 0:
            return obj.comment[:30] + ("..." if len(obj.comment) > 30 else "")
        return "（无评论）"

    get_comment_preview.short_description = "评论"


@admin.register(Movie_hot)
class MovieHotAdmin(admin.ModelAdmin):
    """热门电影管理"""
    list_display = ('id', 'get_movie_name', 'get_movie_imdb_id', 'rating_number', 'get_movie_avg_score')
    list_display_links = ('get_movie_name',)
    search_fields = ('movie__name',)
    list_per_page = 20
    ordering = ('-rating_number',)

    def get_movie_name(self, obj):
        return obj.movie.name

    get_movie_name.short_description = "电影名"

    def get_movie_imdb_id(self, obj):
        return obj.movie.imdb_id

    get_movie_imdb_id.short_description = "IMDB ID"

    def get_movie_avg_score(self, obj):
        score = obj.movie.get_score()
        return f"{score:.1f}" if score else "无评分"

    get_movie_avg_score.short_description = "平均分"

    # 自定义操作
    actions = ['recalculate_hot_movies']

    def recalculate_hot_movies(self, request, queryset):
        """手动重新计算热门电影"""
        from django.db.models import Count

        # 清空现有数据
        Movie_hot.objects.all().delete()

        # 获取评分最多的电影
        hot_movies = Movie.objects.annotate(
            rating_count=Count('movie_rating')
        ).order_by('-rating_count')[:100]

        # 重新创建热门电影记录
        for movie in hot_movies:
            Movie_hot.objects.create(
                movie=movie,
                rating_number=movie.rating_count
            )

        count = len(hot_movies)
        self.message_user(request, f"已重新计算热门电影，共更新{count}部电影")

    recalculate_hot_movies.short_description = "重新计算热门电影"