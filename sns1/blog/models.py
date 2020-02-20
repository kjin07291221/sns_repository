from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
# Create your models here.


class CustomUserManager(UserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
             'Designates whether the user can log into this admin site.),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    


class Category(models.Model):

    name = models.CharField('タイトル', max_length=255)



    def __str__(self):

        return self.name


class PostQuerySet(models.QuerySet):

    def pubulished(self):

        return self.filter(create_at__lte=timezone.now())


class Post(models.Model):

    title = models.CharField('タイトル', max_length=32)

    thumbnail = models.ImageField('サムネイル')

    text = models.TextField('本文')

    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='カテゴリ')

    create_at = models.DateTimeField('作成日', default=timezone.now)



    objects = PostQuerySet.as_manager()



    def __str__(self):

        return self.title


class Comment(models.Model):
    name = models.CharField('名前', max_length=255, default='名無し')
    text = models.TextField('本文')
    target = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='対象投稿')
    created_at = models.DateTimeField('作成日', default=timezone.now)
    email = models.EmailField('メールアドレス', blank=True, help_text='入力しておくと、返信があった際に通知します。コメント欄には表示されません。')

    def __str__(self):
        return self.text[:20]


class Reply(models.Model):
    name = models.CharField('名前', max_length=255, default='名無し')
    text = models.TextField('本文')
    target = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='対象コメント')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.text[:20]


class EmailPush(models.Model):
    mail = models.EmailField('メールアドレス', unique=True)
    is_active = models.BooleanField('有効フラグ', default=False)

    def __str__(self):
        return self.email
