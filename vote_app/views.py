# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Vote, Option, VoteHistory
from .forms import VoteForm, OptionForm, VoteAccessForm
from django.contrib.auth.decorators import login_required
@login_required
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

def vote_detail(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    history = VoteHistory.objects.filter(vote=vote)

    # Cek apakah user memiliki akses ke vote ini
    if not request.session.get(f'vote_{vote.id}_access'):
        return HttpResponseForbidden("Masukkan kunci yang benar untuk mengakses vote ini")

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

    return render(request, 'vote_detail.html', {'vote': vote, 'total_votes': total_votes, 'history': history})

def vote_list(request):
    votes = Vote.objects.all().order_by('-id')
    return render(request, 'vote_list.html', {'votes': votes})

# @login_required
# def vote_history(request, vote_id):
#     vote = get_object_or_404(Vote, id=vote_id)
#     history = VoteHistory.objects.filter(vote=vote)
    
#     if not request.session.get(f'vote_{vote.id}_access'):
#         return HttpResponseForbidden("You must enter the correct key to access this vote history.")

#     return render(request, 'vote_history.html', {'vote': vote, 'history': history})
