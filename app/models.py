from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
#form
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Kiểm tra nếu tên người dùng đã tồn tại trong hệ thống
        if User.objects.filter(username=username).exists():
            raise ValidationError("Tên người dùng đã tồn tại")
        return username

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     # Kiểm tra nếu email đã tồn tại trong hệ thống
    #     if User.objects.filter(email=email).exists():
    #         raise ValidationError("Email này đã được sử dụng")
    #     return email
# Create your models here.
class Category(models.Model):
    sub_category = models.ForeignKey('self',on_delete=models.CASCADE,related_name='sub_categories',null=True,blank=True)
    is_sub = models.BooleanField(default=0)
    name = models.CharField(max_length=200,null=True)
    slug = models.SlugField(max_length=200,unique=True)
    def __str__(self):
        return self.name
    
class Product(models.Model): ##ke thua
    category = models.ManyToManyField(Category,related_name='product')
    name = models.CharField(max_length=200,null=True)
    price = models.FloatField()
    image = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Order(models.Model): ##ke thua
    STATUS_CHOICES = [
        ('cart', 'Chưa hoàn thành'),
        ('pending', 'Chờ xác nhận'),
        ('shipping', 'Chờ giao hàng'),
        ('completed', 'Đã hoàn thành'),
    ]
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='cart')
    transaction_id = models.CharField(max_length=200,null=True)

    def __str__(self):
        return str(self.transaction_id)
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

class OrderItem(models.Model): ##ke thua
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
class ShippingAddress(models.Model): ##ke thua
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    name = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=10, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.address




