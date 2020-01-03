import json

from google.appengine.api import urlfetch

from django.http import HttpResponseForbidden, JsonResponse
from django.utils.timesince import timesince

from givefood.func import find_foodbanks
from givefood.models import ApiFoodbankSearch


def api_foodbanks(request):

    lattlong = request.GET.get("lattlong")
    postcode = request.GET.get("postcode")

    if not lattlong and not postcode:
        return HttpResponseForbidden()

    if postcode and not lattlong:
        pc_api_url = "https://api.postcodes.io/postcodes/%s" % (postcode)
        pc_result = urlfetch.fetch(pc_api_url)
        if pc_result.status_code == 200:
            pc_result_json = json.loads(pc_result.content)
            lattlong = "%s,%s" % (pc_result_json["result"]["latitude"],pc_result_json["result"]["longitude"])

    foodbanks = find_foodbanks(lattlong, 10)
    response_list = []

    if postcode:
        query_type = "postcode"
        query = postcode
    else:
        query_type = "lattlong"
        query = lattlong

    api_hit = ApiFoodbankSearch(
        query_type = query_type,
        query = query,
        nearest_foodbank = foodbanks[0].distance_m,
    )
    api_hit.save()

    for foodbank in foodbanks:
        response_list.append({
            "name":foodbank.name,
            "distance_m":int(foodbank.distance_m),
            "distance_mi":round(foodbank.distance_mi,2),
            "url":foodbank.url,
            "shopping_list_url":foodbank.shopping_list_url,
            "phone":foodbank.phone_number,
            "address":foodbank.full_address(),
            "postcode":foodbank.postcode,
            "country":foodbank.country,
            "charity_number":foodbank.charity_number,
            "charity_register_url":foodbank.charity_register_url(),
            "needs":foodbank.latest_need_text(),
            "number_needs":foodbank.latest_need_text().count('\n')+1,
            "updated":str(foodbank.latest_need_date()),
            "updated_text":timesince(foodbank.latest_need_date()),
        })

    return JsonResponse(response_list, safe=False)
