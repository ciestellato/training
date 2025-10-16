from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
def test_veiw(request):
    return HttpResponse('employee test')