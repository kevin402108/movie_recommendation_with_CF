# movie/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Genre, Movie, Movie_similarity, User, Movie_rating, Movie_hot
from django.contrib.auth.models import Group

admin.site.unregister(Group)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """电影类别管理"""
    list_display = ('id', 'name', 'get_movie_count')
    list_display_links = ('name',)
    search_fields = ('id', 'name')
    list_per_page = 15
    ordering = ('id',)

    def get_movie_count(self, obj):
        """获取该类型下的电影数量"""
        return obj.movie_set.count()
    get_movie_count.short_description = "电影数量"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """电影管理"""
    # 列表页配置
    list_display = ('id', 'name', 'imdb_id', 'release_time', 'director',
                    'get_genre_display', 'get_avg_score', 'get_rating_count', 'get_similar_movies_count')
    list_display_links = ('name',)
    list_filter = ('director','release_time',)
    search_fields = ('id','name','director','imdb_id')
    list_per_page = 10

    # 编辑页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'imdb_id', 'time', 'release_time')
        }),
        ('详情信息', {
            'fields': ('genre', 'intro', 'director', 'writers', 'actors'),
        }),
    )

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
    list_display = ('id', 'movie_source', 'movie_target', 'similarity')
    list_filter = ('movie_source', 'movie_target')
    search_fields = ('movie_source__name',)
    list_per_page = 15
    ordering = ('-similarity',)
    readonly_fields = ('similarity','movie_source','movie_target')

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """用户管理"""
    list_display = ('id', 'name', 'email', 'get_rating_count')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_per_page = 15

    fieldsets = (
        ('个人信息', {
            'fields': ('name', 'email','password')
        }),
    )

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
    list_per_page = 15
    readonly_fields = ('user', 'movie', 'score', 'comment')

    def get_user(self, obj):
        return obj.user.name
    get_user.short_description = "用户名"

    def get_movie(self, obj):
        return obj.movie.name
    get_movie.short_description = "电影名"

    def get_comment_preview(self, obj):
        """评论内容预览（最多显示30字符）"""
        if obj.comment and len(obj.comment) > 0:
            return obj.comment[:30] + ("..." if len(obj.comment) > 30 else "")
        return "（无评论）"
    get_comment_preview.short_description = "评论"

    def has_add_permission(self, request):
        return False



@admin.register(Movie_hot)
class MovieHotAdmin(admin.ModelAdmin):
    """热门电影管理"""
    list_display = ('id', 'get_movie_name', 'get_movie_imdb_id', 'rating_number', 'get_movie_avg_score')
    search_fields = ('movie__name',)
    list_per_page = 15
    ordering = ('-rating_number',)
    readonly_fields = ('movie','rating_number',)

    def get_movie_name(self, obj):
        return obj.movie.name

    get_movie_name.short_description = "电影名"

    def get_movie_imdb_id(self, obj):
        return obj.movie.imdb_id

    get_movie_imdb_id.short_description = "IMDB ID"

    def get_movie_avg_score(self, obj):
        score = obj.movie.get_score()
        return f"{score:.1f}" if score else "无评分"

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    get_movie_avg_score.short_description = "平均分"






