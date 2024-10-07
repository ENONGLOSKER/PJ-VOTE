# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Vote, Option, VoteHistory
from .forms import VoteForm, OptionForm, VoteAccessForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect


@login_required
@csrf_exempt
def like_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    
    if vote.likes.filter(id=request.user.id).exists():
        # Jika user sudah like, maka hapus like (unlike)
        vote.likes.remove(request.user)
    else:
        # Jika user belum like, tambahkan like
        vote.likes.add(request.user)

    return redirect('vote_list')

@login_required
@csrf_exempt 
def create_vote(request):
    if request.method == 'POST':
        vote_form = VoteForm(request.POST)
        if vote_form.is_valid():
            vote = vote_form.save()
            return redirect('add_options', vote_id=vote.id)
    else:
        vote_form = VoteForm()
    return render(request, 'form_vote.html', {'vote_form': vote_form})

@login_required
@csrf_exempt
def add_options(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    options = vote.options.count()
    if request.method == 'POST':
        option_form = OptionForm(request.POST)
        if option_form.is_valid():
            option = option_form.save(commit=False)
            option.vote = vote
            option.save()
            return redirect('add_options', vote_id=vote.id)
    else:
        option_form = OptionForm()
    return render(request, 'form_option.html', {'vote': vote, 'option_form': option_form, 'options': options})
@login_required
@csrf_exempt
def access_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    if request.method == 'POST':
        form = VoteAccessForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            if key == vote.key:
                request.session[f'vote_{vote.id}_access'] = True 
                return redirect('vote_detail', vote_id=vote.id)
            else:
                form.add_error('key', 'Kunci Tidak Valid!')
    else:
        form = VoteAccessForm()
    return render(request, 'access_vote.html', {'form': form, 'vote': vote})

@login_required
@csrf_exempt
def vote_detail(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    history = VoteHistory.objects.filter(vote=vote)

    # Cek apakah user memiliki akses ke vote ini
    # if not request.session.get(f'vote_{vote.id}_access'):
    #     return HttpResponseForbidden("Masukkan kunci yang benar untuk mengakses vote ini")

    total_votes = vote.total_votes()

    # Cek apakah batas waktu sudah habis
    is_deadline_passed = False
    # if vote.deadline and timezone.now() > vote.deadline:
    #     is_deadline_passed = True
    print(is_deadline_passed)
    if request.method == 'POST' and not is_deadline_passed:  # Cek jika deadline belum habis
        option_id = request.POST.get('option')
        option = get_object_or_404(Option, id=option_id)

        # Cek apakah user sudah pernah melakukan vote
        user_vote_history = VoteHistory.objects.filter(user=request.user, vote=vote).first()

        if user_vote_history:
            # Jika user memilih opsi yang sama, jangan lakukan apa-apa
            if user_vote_history.option == option:
                return redirect('vote_detail', vote_id=vote.id)
            
            # Kurangi jumlah vote dari opsi sebelumnya
            previous_option = user_vote_history.option
            previous_option.votes -= 1
            previous_option.save()

            # Update ke opsi baru
            user_vote_history.option = option
            user_vote_history.save()
        else:
            # Buat vote baru jika belum pernah vote
            VoteHistory.objects.create(user=request.user, vote=vote, option=option)
        
        # Tambahkan vote ke opsi baru
        option.votes += 1
        option.save()

        return redirect('vote_detail', vote_id=vote.id)

    return render(request, 'vote_detail.html', {
        'vote': vote, 
        'total_votes': total_votes, 
        'history': history,
        'is_deadline_passed': is_deadline_passed  # Tambahkan flag untuk template
    })

@login_required
@csrf_exempt
def vote_detail(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    history = VoteHistory.objects.filter(vote=vote)

    # Cek apakah vote sudah melewati deadline
    is_deadline_passed = vote.deadline and timezone.now() > vote.deadline
    
    total_votes = vote.total_votes()

    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(Option, id=option_id)

        # Cek apakah user sudah pernah melakukan vote
        user_vote_history = VoteHistory.objects.filter(user=request.user, vote=vote).first()

        if user_vote_history:
            # Jika user memilih opsi yang sama, jangan lakukan apa-apa
            if user_vote_history.option == option:
                return redirect('vote_detail', vote_id=vote.id)
            
            # Kurangi jumlah vote dari opsi sebelumnya
            previous_option = user_vote_history.option
            previous_option.votes -= 1
            previous_option.save()

            # Update ke opsi baru
            user_vote_history.option = option
            user_vote_history.save()
        else:
            # Buat vote baru jika belum pernah vote
            VoteHistory.objects.create(user=request.user, vote=vote, option=option)
        
        # Tambahkan vote ke opsi baru
        option.votes += 1
        option.save()

        return redirect('vote_detail', vote_id=vote.id)

    return render(request, 'vote_detail.html', {'vote': vote, 'total_votes': total_votes, 'history': history, 'is_deadline_passed': is_deadline_passed})

@csrf_exempt
def vote_list(request):
    votes = Vote.objects.all().order_by('-id')
    return render(request, 'vote_list.html', {'votes': votes})

def get_started(request):
    return render(request, 'get_started.html')

# user logut
def user_logout(request):
    logout(request)
    return redirect('vote_list')  # or any other page you want to redirect to after logout



# @login_required
# def vote_history(request, vote_id):
#     vote = get_object_or_404(Vote, id=vote_id)
#     history = VoteHistory.objects.filter(vote=vote)
    
#     if not request.session.get(f'vote_{vote.id}_access'):
#         return HttpResponseForbidden("You must enter the correct key to access this vote history.")

#     return render(request, 'vote_history.html', {'vote': vote, 'history': history})
