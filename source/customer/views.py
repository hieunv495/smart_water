from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from functools import reduce
import json
from main.models import IssueMessage, AppRate
from django.db.models import Avg
from main.models import DigitalWaterDevice, MechanicsWaterDevice, MechanicsWaterDeviceCollect
from random import randint
import datetime


def home(request):

    water_bills = request.user.customer_profile.water_bills.all()
    owe_bills = request.user.customer_profile.water_bills.filter(is_paid=False)
    debt = reduce(lambda s, b: s + b.total, list(owe_bills), 0)

    return render(request, 'customer/customer_home.html', {
        'water_bills': water_bills,
        'owe_bills': owe_bills,
        'debt': debt
    })


def device_management(request):
    if not request.user.is_authenticated() or not request.user.is_customer:
        return HttpResponse('Chi danh cho Customer')

    digital_devices = request.user.customer_profile.digital_water_devices.all()
    mechanics_devices = request.user.customer_profile.mechanics_water_devices.all()

    return render(request, 'customer/device_management.html', {
        'digital_devices': digital_devices,
        'mechanics_devices': mechanics_devices
    })


def device_info(request, device_type=None, device_token=None):
    if not request.user.is_authenticated() or not request.user.is_customer:
        return HttpResponse('Chi danh cho Customer')

    device = None

    print(device_type)
    print(device_token)
    if device_type == 'digital':
        device = get_object_or_404(DigitalWaterDevice, token=device_token)
    elif device_type == 'mechanics':
        device = get_object_or_404(MechanicsWaterDevice, token=device_token)

    collects = None

    if device is not None:
        collects = device.collects.all().order_by('-year', '-month', '-created_at')

    return render(request, 'customer/device_info.html', {
        'device_type': device_type,
        'device': device,
        'collects': collects
    })


def update_mechanics_device_value(request, device_token):

    next = request.GET.get('next',request.get_full_path())

    if not request.user.is_authenticated() or not request.user.is_customer:
        return HttpResponse('Chi danh cho Customer')
    customer = request.user.customer_profile

    device = get_object_or_404(
        MechanicsWaterDevice, customer=customer, token=device_token)

    if request.method == 'POST':
        image = request.FILES.get('image')
        value = request.POST.get('value')
        print(image)
        print(value)
        if image is not None and value is not None:
            now = datetime.datetime.now()
            month = now.month
            year = now.year
            MechanicsWaterDeviceCollect.objects.create(
                month=month, year=year, device=device,image=image, value=value)
            return redirect(next)
        else:
            return render(request, 'customer/update_mechanics_device_value.html', {
                'device': device
            })
    return render(request, 'customer/update_mechanics_device_value.html', {
        'device': device
    })

@csrf_exempt
def api_parse_image_device_value(request):

    image = request.FILES.get('image')
    value = randint(20, 200)
    res = {
        'value': value
    }
    return HttpResponse(json.dumps(res), content_type='application/json')


def issue_message(request):
    if not request.user.is_authenticated() or not request.user.is_customer:
        return HttpResponse('Chi danh cho Customer')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        IssueMessage.objects.create(
            customer=request.user.customer_profile, title=title, content=content)

        return render(request, 'customer/issue_message.html', {
            'messages': request.user.customer_profile.issue_messages.all()
        })
    else:
        return render(request, 'customer/issue_message.html', {
            'messages': request.user.customer_profile.issue_messages.all()
        })


def contact(request):
    return render(request, 'customer/contact.html', {})


def rate(request):
    if not request.user.is_authenticated() or not request.user.is_customer:
        return HttpResponse('Chi danh cho Customer')

    my_rate = None
    if hasattr(request.user.customer_profile, 'app_rate'):
        my_rate = request.user.customer_profile.app_rate

    if request.method == 'POST':
        rate = int(request.POST.get('rate'))
        message = request.POST.get('message')

        if my_rate is None:
            my_rate = AppRate()
            my_rate.customer = request.user.customer_profile

        my_rate.rate = rate
        my_rate.message = message
        my_rate.save()

    app_rates = AppRate.objects.all()

    avg_rate = AppRate.objects.all().aggregate(Avg('rate'))['rate__avg']

    return render(request, 'customer/rate.html', {
        'my_rate': my_rate,
        'avg_rate': avg_rate,
        'app_rates': app_rates
    })
