from django.shortcuts import render
import django.template
import django.http

#TODO Might be worth to find a cleaner way to import this.
import sys
sys.path.insert(0, r"C:\Users\simon\Coding\ML\FindSimilarPapers\dewey\src")
sys.path.insert(0, r"C:\Users\simon\Coding\ML\FindSimilarPapers\dewey\src\deweyengine")
import deweyengine.similar_papers_service

similar_papers_service = deweyengine.similar_papers_service.SimilarPapersService()

# Create your views here.
def index(request):

    if request.method == 'POST':
        query = request.POST.get('query', None)

        # Get papers by similarity 
        result_list = [x[0] for x in similar_papers_service.get_papers_by_similarity(query)]
    else:
        result_list = [x[0] for x in similar_papers_service.get_papers_by_similarity('debug')]
    
    template = django.template.loader.get_template('searchinterface/index.html')
    context = {
        'result_list': result_list
    }
    return django.http.HttpResponse(template.render(context, request))