const status = document.querySelector("#status");
const uml_btn = document.querySelector("#usemylocationbtn");
const addressgo_btn = document.querySelector("#addressgobtn");
const address_field = document.querySelector("#address_field");
const results_table = document.querySelector("table");
const api_url_root = "/api/1/foodbanks/search/";

const working_html = "<img src='/static/img/loading.gif' alt='Loading'> Getting nearby foodbanks...";
const requesting_loc_html = "<img src='/static/img/loading.gif' alt='Loading'> Requesting your location...";
const no_loc_apology_text = "Sorry, we tried to get your location automatically but couldn't. Try a postcode or address.";
const no_addr_text = "Did you forget to enter an address?";
const nothing_needed_text = "Nothing right now, thanks";
const need_unknown_text = "Sorry. We don't know what's needed here, please contact the food bank";

function init() {
  var input = address_field;
  var options = {
    types: ["geocode"]
  };

  autocomplete = new google.maps.places.Autocomplete(input, options);
  autocomplete.setComponentRestrictions({'country': ['gb']});
  uml_btn.addEventListener("click", do_geolocation);
  addressform.addEventListener("submit", do_address);
  preload_image("/static/img/loading.gif");
}

function do_geolocation(event) {
  clear_results();
  if (!navigator.geolocation) {
    status.textContent = no_loc_apology_text;
    uml_btn.style.display = "none";
  } else {
    status.innerHTML = requesting_loc_html;
    navigator.geolocation.getCurrentPosition(
      do_lattlong,
      function() {
        status.textContent = no_loc_apology_text;
      }
    );
  }
  event.preventDefault();
}

function do_address(event) {
  clear_results();
  address = address_field.value;
  if (address == "") {
    status.textContent = no_addr_text;
  } else {
    querystring = "?address=" + address;
    api_url = api_url_root + querystring;
    api_request(api_url);
    record_search(querystring);
    history.pushState({address: address}, "address", querystring)
  }
  event.preventDefault();
}

function do_lattlong(position) {
  latt  = position.coords.latitude;
  long = position.coords.longitude;
  address_field.value = ""
  querystring = "?lattlong=" + latt + "," + long;
  api_url = api_url_root + querystring;
  api_request(api_url);
  record_search(querystring);
  history.pushState({lattlong: latt + "," + long}, "lattlong", querystring)
}

function record_search(querystring) {
  gtag('config', 'UA-153866507-1', {
    'page_title' : 'What Food Banks Need',
    'page_path': '/needs/' + querystring
  });
}

function api_request(url) {
  status.innerHTML = working_html;
  var fb_req = new XMLHttpRequest();
  fb_req.addEventListener("load", api_response);
  fb_req.responseType = "json";
  fb_req.open("GET", url);
  fb_req.send();
}

function clear_results() {
  while (results_table.firstChild) {
    results_table.removeChild(results_table.firstChild);
  }
}

function api_response() {

  template = document.querySelector("#fb_row");

  for (i in this.response) {

    foodbank = this.response[i];

    url = foodbank.shopping_list_url;
    name = foodbank.name;
    distance = foodbank.distance_mi;
    slug = foodbank.slug;
    number_needs = foodbank.number_needs;
    phone = foodbank.phone;
    needs = foodbank.needs;
    needs_html = needs.replace(/\n/g, "<br>");

    currentrow = document.importNode(template.content, true);
    currentrow.querySelector("a.foodbank").href = "/needs/click/" + slug + "/";
    currentrow.querySelector("a.foodbank").textContent = name;
    currentrow.querySelector(".distance span").textContent = distance;
    if (number_needs > 0 && needs != "Nothing" && needs != "Unknown") {
      if (number_needs > 1) {item_text = "items"} else {item_text = "item"};
      currentrow.querySelector(".fb_needs p").innerHTML = needs_html;
    } else if (needs == "Unknown") {
      currentrow.querySelector(".fb_needs").innerHTML = need_unknown_text;
    } else {
      currentrow.querySelector(".fb_needs").innerHTML = nothing_needed_text;
    }
    if (currentrow.querySelector(".links")) {
      currentrow.querySelector(".links .phone").href = "tel:" + phone
      currentrow.querySelector(".links .info").href = "/needs/at/" + slug + "/";
    }
    results_table.appendChild(currentrow);
  }

  status.innerHTML = "";
}

function preload_image(url) {
    img = new Image();
    img.src = url;
}

init();
