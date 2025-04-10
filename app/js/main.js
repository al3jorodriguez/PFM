"use strict";
require([
  "esri/Map",
  "esri/views/MapView",
  "esri/layers/FeatureLayer",
  "esri/rest/geoprocessor",
  "esri/widgets/Legend",
  "esri/widgets/LayerList",
  "esri/widgets/ScaleBar",
  "esri/widgets/Measurement",
  "esri/widgets/Expand",
  "esri/widgets/FeatureTable",
], function (
  Map,
  MapView,
  FeatureLayer,
  Geoprocessor,
  Legend,
  LayerList,
  ScaleBar,
  Measurement,
  Expand,
  FeatureTable
) {
  const map = new Map({
    basemap: "topo-vector",
  });

  const view = new MapView({
    container: "mapViewDiv",
    map: map,
    center: [-4.453, 36.72947],
    zoom: 10,
  });

  const capaRiesgoInundacion = new FeatureLayer({
    url: "https://desktop-dakg3p7/server/rest/services/PFM/Riesgos/FeatureServer/4",
    popupTemplate: {
      title: "Información de referencia ",
      content: `
        <b>Unidad Censal:</b> {codigo}<br>
        <b>Riesgo:</b> {riesgo} <br>
        <b>Hombres: {total_hombre}</b>
        <b>Mujeres: {total_mujer}</b>
      `,
    },
  });

  const capaRiesgoIslas = new FeatureLayer({
    url: "https://desktop-dakg3p7/server/rest/services/PFM/Riesgos/FeatureServer/5",
    popupEnabled: true,
  });

  map.addMany([capaRiesgoInundacion, capaRiesgoIslas]);

  const gpUrlInundacion =
    "https://desktop-dakg3p7/server/rest/services/PFM/MapaInundacion/GPServer/Mapa%20Inundacion";
  const paramsInundacion = {
    Nombre_PDF: "featureSet",
    Autor: "vsDistance",
  };
  const gpUrlIslas =
    "https://desktop-dakg3p7/server/rest/services/PFM/MapaIslas/GPServer/Mapa%20Islas";
  const paramsIslas = {
    Nombre_PDF: "featureSet",
    Autor: "vsDistance",
  };

  const btnInundacion = document.getElementById("btnInundacion");
  const btnIslaCalor = document.getElementById("btnIslaCalor");

  // Lógica para ejecutar geoprocesos
  btnInundacion.addEventListener("click", function () {
    showLoader(true);
    Geoprocessor.submitJob(gpUrlInundacion, paramsInundacion).then(
      ejecutarGeoproceso
    );
  });

  btnIslaCalor.addEventListener("click", function () {
    showLoader(true);
    Geoprocessor.submitJob(gpUrlIslas, paramsIslas).then(ejecutarGeoproceso);
  });

  function ejecutarGeoproceso(jobInfo) {
    const jobid = jobInfo.jobId;
    console.log("ArcGIS Server job ID: ", jobid);

    const options = {
      interval: 1500,
      statusCallback: (j) => {
        console.log("Job Status: ", j.jobStatus);
      },
    };

    jobInfo.waitForJobCompletion(options).then(() => {
      jobInfo
        .fetchResultData("PDF")
        .then(function (result) {
          const pdfUrl = result.value.url;
          mostrarEnlacePDF(pdfUrl);
          showLoader(false);
        })
        .catch(function (error) {
          console.error("Error obteniendo el resultado:", error);
          showLoader(false);
        });
      const outputUrl = jobInfo;
      mostrarEnlacePDF(outputUrl);
    });
  }

  function mostrarEnlacePDF(url) {
    // Crear contenedor para el resultado con botón de cierre
    const container = document.getElementById("resultados");

    // Crear el botón de cierre
    const closeButton = document.createElement("button");
    closeButton.textContent = "X";
    closeButton.classList.add("btn-danger", "close-btn");
    closeButton.style.float = "right"; // Para posicionar la "X" en la esquina superior derecha
    closeButton.addEventListener("click", function () {
      // Ocultar el contenedor de resultados y mostrar nuevamente los botones
      container.style.display = "none";
    });

    container.innerHTML = `
    <p><strong>Resultado disponible:</strong></p>
    <a class='download' href="${url}" target="_blank">Ver/Descargar PDF</a>
    `;
    container.appendChild(closeButton); // Añadir el botón de cierre
    container.style.display = "block";
  }
  function showLoader(active) {
    const loader = document.getElementById("loader");
    active ? (loader.style.display = "block") : (loader.style.display = "none");
  }

  // Widgets del visor
  view.when(async () => {
    const legend = new Legend({ view });
    const layerList = new LayerList({ view });
    const scaleBar = new ScaleBar({ view });

  
    // Agrega los widgets con Expand
    view.ui.add(
      new Expand({
        view,
        content: legend,
        group: "top-right",
        expanded: false,
      }),
      "top-right"
    );
    view.ui.add(
      new Expand({
        view,
        content: layerList,
        group: "top-right",
        expanded: false,
      }),
      "top-right"
    );
    view.ui.add(scaleBar, { position: "bottom-left" });
  
    layerList.when(() => {
      showLoader(false);
    });
  });
  
});
