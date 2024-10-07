// Inicializa o mapa
var map2 = L.map('map2').setView([-22.9068, -43.1729], 13);
var marker2 = L.marker([-22.9068, -43.1729]).addTo(map2);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map2);

// Adiciona um evento de clique ao mapa
map2.on('click', function (e) {
  var lat = e.latlng.lat;
  var lng = e.latlng.lng;

  // Atualiza o formulário com as coordenadas clicadas
  document.getElementById('inputLat').value = lat;
  document.getElementById('inputLng').value = lng;

  // Atualiza o mapa e o marcador com a localização clicada
  marker2.setLatLng([lat, lng]).addTo(map2);
  map2.setView([lat, lng], 13);
});

// Função para atualizar o mapa com a localização digitada
document.getElementById('locationForm').addEventListener('submit', function (e) {
  e.preventDefault(); // Evita o envio do formulário

  var lat = parseFloat(document.getElementById('inputLat').value);
  var lng = parseFloat(document.getElementById('inputLng').value);

  if (!isNaN(lat) && !isNaN(lng)) {
    // Atualiza o mapa com a nova localização
    map2.setView([lat, lng], 13);
    marker2.setLatLng([lat, lng]).addTo(map2);
  } else {
    alert('Por favor, insira coordenadas válidas.');
  }
});

// Define opções para a geolocalização do navegador
var options = {
  enableHighAccuracy: true,
  timeout: 5000,
  maximumAge: 0,
};

// Função de sucesso da geolocalização para o mapa
function success2(pos) {
  var crd = pos.coords;
  var userLocation2 = [crd.latitude, crd.longitude];
  map2.setView(userLocation2, 13);
  marker2.setLatLng(userLocation2).addTo(map2);
}

function error2(err) {
  console.warn(`ERRO(${err.code}): ${err.message}`);
}

// Tenta obter a localização atual do usuário para o mapa
navigator.geolocation.getCurrentPosition(success2, error2, options);
