from django.contrib import admin
from django.urls import path, reverse
from . import views

app_name = 'movie'

# 系统后台admin配置
admin.site.site_header = '电影推荐系统后台' # 后台首页头部标题
admin.site.site_title = '电影推荐系统后台' # 后台浏览器标签标题
admin.site.index_title = '首页' # 后台首页标题
admin.site.site_url = '/movie' # 系统首页链接
# admin.site.enable_nav_sidebar = False 是否启用侧边栏导航(Django 3.0以上版本可用)
admin.site.empty_value_display = '暂无数据' # 后台空值显示
admin.site.login_template = 'admin/login.html' # 后台登录页
admin.site.index_template = 'admin/index.html' # 后台首页
admin.site.logout_template = 'registration/logged_out.html' # 后台退出登录页
admin.site.password_change_template = 'registration/password_change_form.html' # 后台修改密码页
admin.site.password_change_done_template = 'registration/password_change_done.html' # 后台修改密码成功页

urlpatterns = [
    # 默认首页
    path('', views.IndexView.as_view(), name='index'),
    # 热门电影
    path('hot', views.PopularMovieView.as_view(), name='hot'),
    # 登录
    path('login', views.LoginView.as_view(), name='login'),
    # 退出
    path('logout', views.UserLogout, name='logout'),
    # 注册
    path('register', views.RegisterView.as_view(), name='register'),
    # 分类查看
    path('tag', views.TagView.as_view(), name='tag'),
    # 搜索功能
    path('search', views.SearchView.as_view(), name='search'),
    # 电影详情页面
    path('detail/<int:pk>', views.MovieDetailView.as_view(), name='detail'),
    # 评分历史页面
    path('history/<int:pk>', views.RatingHistoryView.as_view(),name='history'),
    # 删除记录
    path('del_rec/<int:pk>',views.delete_recode,name='delete_record'),
    # 推荐页面
    path('recommend/',views.RecommendMovieView.as_view(),name='recommend'),
    # 导入物品之间的相似度
    # path('calc_movie_similarity',views.calc_movie_similarity,name='calc_similarity')

]