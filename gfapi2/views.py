from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseBadRequest

from givefood.models import Foodbank, ApiFoodbankSearch, FoodbankChange, ParliamentaryConstituency
from .func import ApiResponse
from givefood.func import get_all_foodbanks, find_foodbanks, geocode

DEFAULT_FORMAT = "json"


def index(request):
        
    template_vars = {}

    return render_to_response("index.html", template_vars, context_instance=RequestContext(request))


def docs(request):

    api_formats = ["JSON","XML","YAML"]

    eg_foodbanks = [
        "Sid Valley",
        "Kingsbridge",
        "Norwood & Brixton",
        "Black Country",
    ]

    eg_searches = {
        "address":"12 Millbank, Westminster, London SW1P 4QE",
        "address":"Mount Pleasant Rd, Porthleven, Helston TR13 9JS",
        "lat_lng":"51.178889,-1.826111",
        "lat_lng":"52.090833,0.131944",
    }

    eg_parl_cons = {
        "Uxbridge and South Ruislip",
        ""
    }
    
    template_vars = {
        "api_formats":api_formats,
        "eg_foodbanks":eg_foodbanks,
        "eg_searches":eg_searches,
        "eg_parl_cons":eg_parl_cons,
    }

    return render_to_response("docs.html", template_vars, context_instance=RequestContext(request))

def foodbanks(request):

    format = request.GET.get("format", DEFAULT_FORMAT)

    foodbanks = get_all_foodbanks()
    response_list = []

    for foodbank in foodbanks:
        response_list.append({
            "name":foodbank.name,
            "alt_name":foodbank.alt_name,
            "slug":foodbank.slug,
            "phone":foodbank.phone_number,
            "secondary_phone":foodbank.secondary_phone_number,
            "email":foodbank.contact_email,
            "address":foodbank.full_address(),
            "postcode":foodbank.postcode,
            "closed":foodbank.is_closed,
            "country":foodbank.country,
            "lat_lng":foodbank.latt_long,
            "network":foodbank.network,
            "created":foodbank.created,
            "modified":foodbank.modified,
            "created":foodbank.created,
            "urls": {
                "self":"https://www.givefood.org.uk/api/2/foodbank/%s/" % (foodbank.slug),
                "html":"https://www.givefood.org.uk/needs/at/%s/" % (foodbank.slug),
                "homepage":foodbank.url,
                "shopping_list":foodbank.shopping_list_url,
            },
            "charity": {
                "registration_id":foodbank.charity_number,
                "register_url":foodbank.charity_register_url(),
            },
            "politics": {
                "parliamentary_constituency":foodbank.parliamentary_constituency,
                "mp":foodbank.mp,
                "mp_party":foodbank.mp_party,
                "mp_parl_id":foodbank.mp_parl_id,
                "ward":foodbank.ward,
                "district":foodbank.district,
                "urls": {
                    "self":"https://www.givefood.org.uk/api/2/constituency/%s/" % (foodbank.parliamentary_constituency_slug),
                    "html":"https://www.givefood.org.uk/needs/in/constituency/%s/" % (foodbank.parliamentary_constituency_slug),
                },
            }
        })

    return ApiResponse(response_list, "foodbanks", format)


def foodbank(request, slug):

    format = request.GET.get("format", DEFAULT_FORMAT)
    foodbank = get_object_or_404(Foodbank, slug = slug)

    # Locations
    locations = foodbank.locations()
    location_list = []
    for location in locations:
        location_list.append(
            {
                "name":location.name,
                "address":location.full_address(),
                "postcode":location.postcode,
                "lat_lng":location.latt_long,
                "phone":location.phone_number,
                "politics": {
                    "parliamentary_constituency":location.parliamentary_constituency,
                    "mp":location.mp,
                    "mp_party":location.mp_party,
                    "ward":location.ward,
                    "district":location.district,
                    "urls": {
                        "self":"https://www.givefood.org.uk/api/2/constituency/%s/" % (location.parliamentary_constituency_slug),
                        "html":"https://www.givefood.org.uk/needs/in/constituency/%s/" % (location.parliamentary_constituency_slug),
                    },
                }
            }
        )

    nearby_foodbank_list = []
    for nearby_foodbank in foodbank.nearby():
        nearby_foodbank_list.append(
            {
                "name":nearby_foodbank.name,
                "slug":nearby_foodbank.slug,
                "urls": {
                    "self":"https://www.givefood.org.uk/api/2/foodbank/%s/" % (nearby_foodbank.slug),
                    "html":"https://www.givefood.org.uk/needs/at/%s/" % (nearby_foodbank.slug),
                    "homepage":nearby_foodbank.url,
                    "shopping_list":nearby_foodbank.shopping_list_url,
                },
                "address":nearby_foodbank.full_address(),
                "lat_lng":nearby_foodbank.latt_long,
            }
        )

    response_dict = {
        "name":foodbank.name,
        "alt_name":foodbank.alt_name,
        "slug":foodbank.slug,
        "phone":foodbank.phone_number,
        "secondary_phone":foodbank.secondary_phone_number,
        "email":foodbank.contact_email,
        "address":foodbank.full_address(),
        "postcode":foodbank.postcode,
        "closed":foodbank.is_closed,
        "lat_lng":foodbank.latt_long,
        "network":foodbank.network,
        "created":foodbank.created,
        "modified":foodbank.modified,
        "urls": {
            "self":"https://www.givefood.org.uk/api/2/foodbank/%s/" % (foodbank.slug),
            "html":"https://www.givefood.org.uk/needs/at/%s/" % (foodbank.slug),
            "homepage":foodbank.url,
            "shopping_list":foodbank.shopping_list_url,
            "map":"https://www.givefood.org.uk/needs/at/%s/map.png" % (foodbank.slug),
        },
        "charity": {
            "registration_id":foodbank.charity_number,
            "register_url":foodbank.charity_register_url(),
        },
        "locations": location_list,
        "politics": {
            "parliamentary_constituency":foodbank.parliamentary_constituency,
            "mp":foodbank.mp,
            "mp_party":foodbank.mp_party,
            "ward":foodbank.ward,
            "district":foodbank.district,
            "urls": {
                "self":"https://www.givefood.org.uk/api/2/constituency/%s/" % (foodbank.parliamentary_constituency_slug),
                "html":"https://www.givefood.org.uk/needs/in/constituency/%s/" % (foodbank.parliamentary_constituency_slug),
            },
        },
        "need": {
            "id":foodbank.latest_need_id(),
            "needs":str(foodbank.latest_need_text()),
            "created":foodbank.latest_need_date(),
            "self":"https://www.givefood.org.uk/api/2/need/%s/" % (foodbank.latest_need_id()),
        },
        "nearby_foodbanks": nearby_foodbank_list,
    }

    return ApiResponse(response_dict, "foodbank", format)


def foodbank_search(request):
    
    format = request.GET.get("format", DEFAULT_FORMAT)
    lat_lng = request.GET.get("lat_lng")
    address = request.GET.get("address")

    if not lat_lng and not address:
        return HttpResponseBadRequest()

    if address and not lat_lng:
        lat_lng = geocode(address)

    foodbanks = find_foodbanks(lat_lng, 10)
    response_list = []

    if address:
        query_type = "address"
        query = address
    else:
        query_type = "lattlong"
        query = lat_lng

    api_hit = ApiFoodbankSearch(
        query_type = query_type,
        query = query,
        nearest_foodbank = foodbanks[0].distance_m,
        latt_long = lat_lng,
    )
    api_hit.save()

    response_list = []

    for foodbank in foodbanks:
        response_list.append({
            "name":foodbank.name,
            "alt_name":foodbank.alt_name,
            "slug":foodbank.slug,
            "phone":foodbank.phone_number,
            "secondary_phone":foodbank.secondary_phone_number,
            "email":foodbank.contact_email,
            "address":foodbank.full_address(),
            "postcode":foodbank.postcode,
            "closed":foodbank.is_closed,
            "lat_lng":foodbank.latt_long,
            "network":foodbank.network,
            "modified":foodbank.modified,
            "created":foodbank.created,
            "distance_m":int(foodbank.distance_m),
            "distance_mi":round(foodbank.distance_mi,2),
            "urls": {
                "self":"https://www.givefood.org.uk/api/2/foodbank/%s/" % (foodbank.slug),
                "html":"https://www.givefood.org.uk/needs/at/%s/" % (foodbank.slug),
                "homepage":foodbank.url,
                "shopping_list":foodbank.shopping_list_url,
                "map":"https://www.givefood.org.uk/needs/at/%s/map.png" % (foodbank.slug),
            },
            "charity": {
                "registration_id":foodbank.charity_number,
                "register_url":foodbank.charity_register_url(),
            },
            "politics": {
                "parliamentary_constituency":foodbank.parliamentary_constituency,
                "mp":foodbank.mp,
                "mp_party":foodbank.mp_party,
                "mp_parl_id":foodbank.mp_parl_id,
                "ward":foodbank.ward,
                "district":foodbank.district,
                "urls": {
                    "self":"https://www.givefood.org.uk/api/2/constituency/%s/" % (foodbank.parliamentary_constituency_slug),
                    "html":"https://www.givefood.org.uk/needs/in/constituency/%s/" % (foodbank.parliamentary_constituency_slug),
                },
            }
        })

    return ApiResponse(response_list, "foodbanks", format)


def needs(request):

    format = request.GET.get("format", DEFAULT_FORMAT)

    needs = FoodbankChange.objects.filter(published = True).order_by("-created")[:100]

    response_list = []

    for need in needs:
        response_list.append({
            "id":need.need_id,
            "created":need.created,
            "foodbank": {
                "name":need.foodbank_name,
                "slug":str(need.foodbank_name_slug()),
                "self":"https://www.givefood.org.uk/api/2/foodbank/%s/" % (need.foodbank_name_slug()),
            },
            "needs":str(need.change_text),
            "url":need.uri,
            "self":"https://www.givefood.org.uk/api/2/needs/%s/" % (need.need_id),
        })

    return ApiResponse(response_list, "needs", format)