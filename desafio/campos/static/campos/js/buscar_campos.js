// static/home/js/map.js

document.addEventListener('DOMContentLoaded', function() {
    // Inicializa o mapa
    var map = L.map('map').setView([-22.9068, -43.1729], 13);

    // Adiciona um tile layer ao mapa utilizando o OpenStreetMap
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Dados dos campos passados para o JavaScript
    var camposData = JSON.parse(document.getElementById('campos-data').textContent);

    console.log('Dados dos campos:', camposData); // Verifica os dados carregados

    // Itera sobre os campos e adiciona os marcadores no mapa
    camposData.forEach(function(campo) {
        var lat = parseFloat(campo.latitude); // Certifica-se de que latitude e longitude são números
        var lng = parseFloat(campo.longitude);
        console.log('Latitude:', lat, 'Longitude:', lng);  // Verifica as coordenadas
        if (!isNaN(lat) && !isNaN(lng)) {  // Verifica se as coordenadas são válidas
            L.marker([lat, lng]).addTo(map)
                .bindPopup('<strong>' + campo.nome + '</strong><br>' + campo.endereco + '<br>' + campo.descricao)
                .openPopup();
        } else {
            console.warn('Coordenadas inválidas:', campo.latitude, campo.longitude);
        }
    });

    // Define opções para a geolocalização do navegador
    var options = {
        enableHighAccuracy: true, 
        timeout: 5000,            
        maximumAge: 0,            
    };

    // Função de sucesso da geolocalização para o mapa
    function success1(pos) {
        var crd = pos.coords;
        console.log('Sua localização atual é:');
        console.log('Latitude : ' + crd.latitude);
        console.log('Longitude: ' + crd.longitude);
        console.log('Precisão : ' + crd.accuracy + ' metros');

        var marker1 = L.marker([crd.latitude, crd.longitude]).addTo(map);
        map.setView([crd.latitude, crd.longitude], 13);
        marker1.bindPopup('Você está aqui!').openPopup();
    }

    // Função de erro da geolocalização
    function error1(err) {
        console.warn('ERRO(' + err.code + '): ' + err.message);
    }

    // Inicia a geolocalização
    navigator.geolocation.getCurrentPosition(success1, error1, options);
});
