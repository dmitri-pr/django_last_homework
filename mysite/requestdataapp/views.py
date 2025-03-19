from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .forms import UserBioForm, UploadFileForm


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data['file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print(f'Saved file {filename}.')
    else:
        form = UploadFileForm()
    context = {
        'form': form,
    }

    return render(
        request, 'requestdataapp/file-upload.html', context=context
    )


def process_get_view(request) -> HttpResponse:
    # Не указываю здесь аннотацию ": HttpRequest" для request, так как в моей версии PyCharm это приводит к ошибке
    # в случае со словарями GET, POST и FILES (вот ссылка на нее: https://youtrack.jetbrains.com/issue/PY-59022)
    a = request.GET.get('a')
    b = request.GET.get('b')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'result': result
    }
    return render(
        request, 'requestdataapp/request-query-params.html', context=context
    )


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        'form': UserBioForm()
    }
    return render(
        request, 'requestdataapp/user-bio-form.html', context=context
    )
