from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Image
from .serializers import PostSerializer, ImageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.conf import settings
from .forms import PostForm  # PostForm 임포트
from django.http import JsonResponse
from rest_framework.decorators import api_view
import uuid
from django.core.files.storage import FileSystemStorage



def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})

class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        author = request.data.get('author')
        title = request.data.get('title')
        text = request.data.get('text')
        created_date = request.data.get('created_date')
        published_date = request.data.get('published_date')
        #image = request.FILES.get('image')  

        post = Post(
            author=author,
            title=title,
            text=text,
            created_date=created_date,
            published_date=published_date,
            #image=image
        )

        post.save()

        images = request.FILES.getlist('images')  # 'images' 키로 여러 파일을 가져옵니다.
        print(f'Uploaded images: {images}')
        if images:
            for image in images:
                Image.objects.create(post=post, image=image)  # 각 이미지를 새로운 Image 모델로 저장

        return Response({"message": "Post created successfully"}, status=status.HTTP_201_CREATED)
    
class BlogImages(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
        
# 추가된 뷰
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def js_test(request):
    return render(request, 'blog/js_test.html')


def photo_blog(request):
    posts = Post.objects.all().order_by('-created_date')  # 최신순으로 정렬
    return render(request, 'blog/photo_blog.html', {'posts': posts})

@api_view(['POST'])
def upload_image(request):
    image_file = request.FILES.get('image')  # 요청에서 이미지 파일을 가져옴
    if image_file:
        unique_filename = f"{uuid.uuid4()}.jpg"
        fs = FileSystemStorage()
        filename = fs.save(unique_filename, image_file)
        image_url = fs.url(filename)
        #image = Image.objects.create(image=image_file)  # 이미지 모델 인스턴스를 생성하고 저장
        # serializer = ImageSerializer(image)  # 직렬화
        return JsonResponse({'success': True, 'url': image_url})
    else:
        return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)