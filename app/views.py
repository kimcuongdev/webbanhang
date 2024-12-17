import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse,JsonResponse
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify


# Create your views here.
#Helper-function hiển thị màu tương ứng trạng thái đơn hàng
def get_status_class(status):
    status_classes = {
        'cart': 'text-danger',
        'pending': 'text-warning',
        'shipping': 'text-primary',
        'completed': 'text-success',
    }
    return status_classes.get(status, 'text-muted')
##Kết thúc hiển thị màu







#Helper-function lấy thông tin hiển thị trạng thái
def get_status_display(status):
    status_display = {
        'cart': 'Chưa hoàn thành',
        'pending': 'Chờ xác nhận',
        'shipping': 'Chờ giao hàng',
        'completed': 'Đã hoàn thành'
    }
    return status_display.get(status)
#Kết thúc lấy thông tin hiển thị trạng thái







#Helper-function Lấy thông tin hiển thị
def get_visibility_context(user):
    context = {
        'login_and_register_button': 'hidden' if user.is_authenticated else 'show',
        'logout_button': 'show' if user.is_authenticated else 'hidden',
        'cart_icon': 'show',
        'don_hang': 'show',
        'manage_option': 'hidden',
        'have_cart_item': 'hidden',
        'cartItems': 0,
        'categories': [],
        'staff_manage':'hidden'
    }
    context['categories'] = Category.objects.filter(is_sub=True)
    if user.username == 'admin':
        context['staff_manage'] = 'show'
    if user.is_superuser:
        context['manage_option'] = 'show'
    if user.is_authenticated:
        try:
            order = Order.objects.get(customer=user, status='cart')
            cart_items = order.get_cart_items
            if cart_items > 0:
                context['have_cart_item'] = 'show'
                context['cartItems'] = cart_items
            else: context['have_cart_item'] = 'hidden'
        except Order.DoesNotExist:
            context['have_cart_item'] = 'hidden'
    else:
        context['cart_icon'] = 'hidden'
        context['don_hang'] = 'hidden'
        context['manage_option'] = 'hidden'
    return context
#Kết thúc lấy thông tin hiển thị








#Giao diện quản lý
def manage(request):
    return render(request, 'app/manage.html')
#Hết giao diện quản lý





#Giao diện danh mục sản phẩm
def category(request):
    active_category_slug = request.GET.get('category', '')
    products = Product.objects.none()  # Khởi tạo mặc định
    if active_category_slug:
        # Lấy danh mục hiện tại dựa trên slug
        active_category = Category.objects.filter(slug=active_category_slug).first()
        print(active_category)
        if active_category:
            # Lấy tất cả danh mục con (bao gồm cả danh mục hiện tại)
            child_categories = Category.objects.filter(
                Q(slug=active_category_slug) | Q(sub_category=active_category)
            )
            # Lọc sản phẩm theo các danh mục này
            products = Product.objects.filter(category__in=child_categories).distinct()
    visibility_context = get_visibility_context(request.user)
    context = {'products': products,
               'active_category': active_category,
               **visibility_context}
    return render(request,'app/category.html',context)
#Hết giao diện danh mục sản phẩm







#Giao diện tìm kiếm
def search(request):
    searched = request.POST.get('searched', '') if request.method == "POST" else ''
    keys = Product.objects.filter(name__icontains=searched)
    products = Product.objects.all()
    visibility_context = get_visibility_context(request.user)
    context = {
        'searched': searched,
        'keys': keys,
        'products': products,
        **visibility_context,
    }
    return render(request, "app/search.html", context)







#Giao diện đăng ký
def register(request):
    print('register')
    cart_icon = 'hidden'
    logout_button = 'hidden'
    login_and_register_button = 'hidden'
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            print('abc')
            form.save()
            return redirect('login')
    context = {'form':form,
               'login_and_register_button':login_and_register_button, 
               'logout_button':logout_button, 
               'cart_icon':cart_icon,
               'don_hang':'hidden',
               'manage_option':'hidden'}
    return render(request,"app/register.html",context)
#Hết giao diện đăng ký







#Giao diện đăng nhập
def loginPage(request):
    print('login')
    cart_icon = 'hidden'
    if request.user.is_authenticated:
        return redirect('home')
    else:
        login_and_register_button = "hidden"
        logout_button = "hidden"
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Tên tài khoản hoặc mật khẩu không đúng!')
    context = {'login_and_register_button': login_and_register_button, 
               'logout_button':logout_button, 
               'cart_icon': cart_icon,
               'don_hang':'hidden',
               'manage_option':'hidden'}
    return render(request,"app/login.html",context)
#Hết giao diện đăng nhập







#Chức năng đăng xuất
def logoutPage(request):
    logout(request)
    return redirect('login')
#Hết chức năng đăng xuất





#Giao diện màn hình chính
def home(request):
    # print('home')
    active_category = request.GET.get('category', '')
    products = Product.objects.all()
    
    visibility_context = get_visibility_context(request.user)
    
    context = {
        'active_category': active_category,
        'products': products,
        **visibility_context,  # Thêm các giá trị hiển thị vào context
    }
    return render(request, "app/home.html", context)
#Hết giao diện màn hình chính






#Giao diện giỏ hàng
def cart(request):
    items = []
    order = {'get_cart_items': 0, 'get_cart_total': 0}
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, status='cart')
        items = order.orderitem_set.all()
    
    visibility_context = get_visibility_context(request.user)
    
    context = {
        'items': items,
        'order': order,
        **visibility_context,
    }
    return render(request, "app/cart.html", context)
#Hết giao diện giỏ hàng







#Giao diện thanh toán
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, status = 'cart')
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # Kiểm tra nếu thông tin vận chuyển không đầy đủ
        if not name or not mobile or not address:
            # Thông báo lỗi nếu cần
            return render(request, "app/checkout.html", {
                'items': items,
                'order': order,
                'error_message': "Vui lòng điền đầy đủ thông tin vận chuyển."
            })
        # Lưu thông tin vận chuyển
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            name=name,
            mobile=mobile,
            address=address,
        )
        # Cập nhật trạng thái đơn hàng
        order.status = 'pending'
        order.save()
        # Chuyển hướng đến trang xác nhận hoặc trang chính
        return redirect('order_confirmation')  # Thay 'order_confirmation' bằng URL của trang bạn muốn chuyển đến.
    active_category = request.GET.get('category', '')
    visibility_context = get_visibility_context(request.user)
    context = {
        'active_category': active_category,
        'items': items,
        'order': order,
        **visibility_context,
    }
    return render(request, "app/checkout.html", context)
#Hết giao diện thanh toán


##Giao diện hoàn thành thanh toán
def order_confirmation(request):
    visibility_context = get_visibility_context(request.user)
    context = {**visibility_context}
    return render(request, "app/order_confirmation.html", context)
##Hết giao diện hoàn thành thanh toán






#Xử lý sự kiện updateItem
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, status = 'cart')
    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('added',safe=False)
#Kết thúc xử lý sự kiện updateItems






#Giao diện xem thông tin đơn hàng
@login_required
def showOrderInfo(request, slug=None):  # Thêm giá trị mặc định cho slug
    # Ánh xạ trạng thái với slug
    slug_to_status = {
        'tat-ca': None,  # Không lọc, lấy tất cả đơn hàng
        'chua-hoan-thanh': 'cart',
        'cho-xac-nhan': 'pending',
        'cho-giao-hang': 'shipping',
        'da-hoan-thanh': 'completed',
    }
    
    # Nếu slug không có, mặc định là 'tat-ca'
    if slug is None:
        slug = 'tat-ca'
    
    # Lấy trạng thái tương ứng với slug
    status_filter = slug_to_status.get(slug)
    
    # Lấy danh sách đơn hàng dựa trên trạng thái
    orders = Order.objects.filter(customer=request.user).order_by('-date_order')
    if status_filter:  # Nếu có trạng thái cụ thể
        orders = orders.filter(status=status_filter)
    
    # Chuẩn bị dữ liệu cho template
    order_data = []
    for order in orders:
        # print(order.shippingaddress_set.all())
        shipping_address = order.shippingaddress_set.first()
        receiver = ''
        if shipping_address:
            receiver = shipping_address.name
        if order.get_cart_items == 0:
            continue
        items = order.orderitem_set.all()
        order_data.append({
            'transaction_id': order.transaction_id,
            'date_order': order.date_order,
            'receiver': receiver,
            'status': get_status_display(order.status),
            'status_class': get_status_class(order.status),
            'total': order.get_cart_total,
            'items': [{
                'product_name': item.product.name,
                'quantity': item.quantity,
                'total_price': item.get_total,
                'image_url': item.product.image.url if item.product.image else 'https://via.placeholder.com/100',
            } for item in items],
        })
    visibility_context = get_visibility_context(request.user)
    context = {
        **visibility_context,
        'order_data': order_data,
        'slug': slug,  # Truyền slug vào template

    }
    return render(request, 'app/order_info.html', context)
#Hết giao diện xem thông tin đơn hàng

#Giao diện quản lý đơn hàng
#Hiển thị quản lý
def manageOrder(request,slug=None):
    if slug == 'cho-xac-nhan':
        orders = Order.objects.filter(status='pending')
    elif slug == 'cho-giao-hang':
        orders = Order.objects.filter(status='shipping')
    elif slug == 'da-hoan-thanh':
        orders = Order.objects.filter(status='completed')
    else:  # Default: 'tat-ca'
        orders = Order.objects.exclude(status='cart')
    order_data = []
    for order in orders:
        shipping_address = ShippingAddress.objects.filter(order=order).first()
        items = order.orderitem_set.all()
        order_data.append({
            'id': order.id,
            'total': order.get_cart_total,
            'status': order.status,
            'status_class': get_status_class(order.status),
            'date_order': order.date_order,
            'customer': order.customer,
            'receiver': shipping_address.name if shipping_address else 'N/A',
            'mobile': shipping_address.mobile if shipping_address else 'N/A',
            'address': shipping_address.address if shipping_address else 'N/A',
            'items': [{
                'product_name': item.product.name if item.product else 'Sản phẩm không tồn tại',
                'quantity': item.quantity,
                'total_price': item.get_total,
                'image_url': item.product.image.url if item.product and item.product.image else '',
            } for item in items]
        })
    visibility_context = get_visibility_context(request.user)
    context={
        'order_data': order_data,
        'slug':slug,
        **visibility_context
    }
    return render(request,'app/order_manage.html',context)
#Thay đổi trạng thái
def update_order_status(request, order_id):
    if request.method == "POST":
        new_status = request.POST.get("status")
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        messages.success(request, "Trạng thái đơn hàng đã được cập nhật.")
    return redirect('order_manage', slug='tat-ca')
#Filter

##Hết giao diện quản lý đơn hàng

##Giao diên quản lý mặt hàng
def manageProduct(request):
    visibility_context = get_visibility_context(request.user)
    products = Product.objects.all()
    context={
        'products':products,
        **visibility_context
    }
    return render(request,'app/product_manage.html', context)

def modifyProduct(request, product_id):
    product = Product.objects.get(id=product_id)
    all_categories = Category.objects.all()
    other_categories = all_categories.exclude(product=product)
    visibility_context = get_visibility_context(request.user)
    if request.method == 'POST':
        category_ids = request.POST.getlist('category')
        product.price = request.POST['price']
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        
        product.category.set(Category.objects.filter(id__in=category_ids))

        return redirect('product_manage')  # Điều hướng về danh sách mặt hàng sau khi lưu
    
    context = {
        'product': product,
        **visibility_context,
        'other_categories': other_categories,
    }
    return render(request, 'app/product_modify.html', context)

def addProduct(request):
    visibility_context = get_visibility_context(request.user)
    if request.method == 'POST':
        name = request.POST['name']
        price = float(request.POST['price'])
        image = request.FILES.get('image', None)
        category_ids = request.POST.getlist('category')
        
        # Tạo mặt hàng mới
        product = Product(name=name, price=price, image=image)
        product.save()
        product.category.set(Category.objects.filter(id__in=category_ids))
        
        return redirect('product_manage')  # Điều hướng về danh sách mặt hàng sau khi thêm
        
    select_categories = Category.objects.filter(is_sub=True)
    context = {'select_categories': select_categories,
               **visibility_context,}
    return render(request, 'app/product_add.html', context)

def addNewCategory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_sub = request.POST.get('is_sub') == 'on'
        category_id = request.POST.get('category') if is_sub else None
        
        # Tạo slug từ tên
        slug = slugify(name)
        
        # Lưu vào cơ sở dữ liệu
        new_category = Category(
            name=name,
            slug=slug,
            is_sub=is_sub,
            sub_category=Category.objects.get(id=category_id) if category_id else None
        )
        new_category.save()
        
        # Redirect sau khi lưu thành công
        return redirect('product_add')  # Cập nhật với URL tương ứng

    visibility_context = get_visibility_context(request.user)
    categories = Category.objects.all()  # Chỉ hiển thị danh mục cha
    context = {
        **visibility_context,
        'categories': categories,
    }
    return render(request, 'app/add_new_category.html', context)

##Hết giao diện quản lý mặt hàng

##Giao diện quản lý nhân viên
@login_required
def manageStaff(request):
    visibility_context = get_visibility_context(request.user)

    # Lấy danh sách tất cả tài khoản
    users = User.objects.exclude(username='admin')

    if request.method == 'POST':
        for user in users:
            permission = request.POST.get(f'permissions_{user.id}')
            if permission == "manager":
                user.is_superuser = True
            else:
                user.is_superuser = False
            user.save()
        return redirect('staff_manage')

    context = {
        'users': users,
        **visibility_context,
    }
    return render(request, 'app/staff_manage.html', context)
##Hết giao diện quản lý nhân viên
