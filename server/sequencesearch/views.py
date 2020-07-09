from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Model
import threading
import json
import os
from .models import SearchSequence
from .genbankhandler import GenBankHandler
from config.settings import get_env_value

class SequenceSearchView(View):
    def __init__(self):
        self.genbank_handler = GenBankHandler()

    def validate_key(self, data):
        if 'key' not in data:
            return HttpResponse(f'Key must be provided', status=403)
        
        key = data['key']
        if not KeyValidationView.key_is_valid(key):
            return HttpResponse(f'Key {key} is incorrect', status=403)

        return None

    def db2response(self, db_entry):
        return {
            'searchedSequence': db_entry.search_sequence,
            'status': db_entry.status,
            'created': db_entry.created.strftime('%x %X %z'),
            'result': db_entry.result,
            'id': db_entry.id
        }

    def get_user_sequences(self, user_id):
        dbdata = SearchSequence.objects.filter(user_id=user_id).order_by('created')

        queries = map(self.db2response, dbdata)
        
        data = {
            'user': user_id,
            'queries': list(queries)
        }

        return data

    def run_query(self, search_sequence, query_id):
        result = self.genbank_handler.search_for_sequence(search_sequence)
        organism_id = f' ({result["organism_id"]})' if 'organism_id' in result else ''
        resultText = f'Organism: {result["organism"]}{organism_id}; ' + \
                     f'Protein: {result["protein_name"]}; ' + \
                     f'Starting at position {result["position"]}'
        
        try:
            dbentry = SearchSequence.objects.get(id=query_id)
            dbentry.result = resultText
            dbentry.status = 'complete'
            dbentry.save()
        except SearchSequence.DoesNotExist as identifier:
            # don't worry if this was already deleted
            pass

    def get(self, request):
        user_id = request.GET['user']
        data = self.get_user_sequences(user_id)

        return JsonResponse(data)

    def post(self, request):
        data = json.loads(request.body)

        validation_response = self.validate_key(data)
        if validation_response is not None:
            return validation_response

        search_sequence=data['searchedSequence']
        new_search = SearchSequence(user_id=data['user'], search_sequence=search_sequence, created=timezone.now(), status='pending')
        new_search.save()

        thread = threading.Thread(target=self.run_query, args=(search_sequence, new_search.id))
        thread.start()
        
        response = self.db2response(new_search)
        return JsonResponse(data=response, status=201)

    def delete(self, request, id):
        data = json.loads(request.body)

        validation_response = self.validate_key(data)
        if validation_response is not None:
            return validation_response

        SearchSequence.objects.get(id=id).delete()
        return HttpResponse(status=204, content_type='application/json')

class KeyValidationView(View):
    @staticmethod
    def key_is_valid(key):
        expected_key = get_env_value('GB_APP_KEY', 'kk')
        return expected_key == key

    def post(self, request):
        data = json.loads(request.body)

        response = {
            'isCorrectKey': self.key_is_valid(data['key'])
        }
        return JsonResponse(data=response)

