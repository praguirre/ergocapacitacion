// static/js/planilla_logic.js

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form[data-confirm-message]').forEach(confirmForm => {
        confirmForm.addEventListener('submit', event => {
            const message = confirmForm.dataset.confirmMessage || '¿Confirmar esta acción?';
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    const form = document.getElementById('planilla2-form');
    if (!form) {
        return; // No estamos en una planilla 2, no hacer nada.
    }

    const planillaType = form.dataset.planillaType;
    const allRadios = form.querySelectorAll('input[type="radio"]');

    function updateResults() {
        // Ocultar todos los cuadros de resultado antes de re-evaluar
        document.querySelectorAll('.result-box').forEach(box => box.style.display = 'none');

        // Llamar a la función de lógica específica para la planilla actual
        switch (planillaType) {
            case '2a': checkPlanilla2A(); break;
            case '2b': checkPlanilla2B(); break;
            case '2c': checkPlanilla2C(); break;
            case '2d': checkPlanilla2D(); break;
            case '2e': checkPlanilla2E(); break;
            case '2f': checkPlanilla2F(); break;
            case '2g': checkPlanilla2G(); break;
            case '2h': checkPlanilla2H(); break;
            case '2i': checkPlanilla2I(); break;
        }
    }

    function getPasoValues(prefix) {
        const radios = form.querySelectorAll(`input[name^="${prefix}"]:checked`);
        const values = Array.from(radios).map(r => r.value === 'True');
        const allAnswered = form.querySelectorAll(`[name^="${prefix}"]`).length / 2 === values.length;
        return { values, allAnswered };
    }

    function getSpecificValue(fieldName) {
        const radio = form.querySelector(`input[name="${fieldName}"]:checked`);
        return radio ? radio.value === 'True' : null;
    }

    // --- LÓGICA PARA CADA PLANILLA ---

    function checkPlanilla2A() {
        const p1 = getPasoValues('p1_');
        if (p1.allAnswered) {
            if (p1.values.every(v => v === false)) { // Todas NO
                document.getElementById('p1-result-all-no').style.display = 'block';
            } else if (getSpecificValue('p1_levanta_mas_25kg')) { // Pregunta 3 es SI
                document.getElementById('p1-result-q3-si').style.display = 'block';
            } else if (p1.values.some(v => v === true)) { // Alguna SI
                document.getElementById('p1-result-any-si').style.display = 'block';
            }
        }
        
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                document.getElementById('p2-result-all-no').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }

    function checkPlanilla2B() {
        const p1 = getPasoValues('p1_');
        if (p1.allAnswered) {
            if (p1.values.every(v => v === false)) {
                document.getElementById('p1-result-all-no').style.display = 'block';
            } else if (getSpecificValue('p1_esfuerzo_supera_34kgf')) {
                 document.getElementById('p1-result-q3-si').style.display = 'block';
            } else {
                 document.getElementById('p1-result-any-si').style.display = 'block';
            }
        }
        
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                document.getElementById('p2-result-all-no').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }
    
    function checkPlanilla2C() {
        const p1 = getPasoValues('p1_');
         if (p1.allAnswered) {
            if (p1.values.every(v => v === false)) {
                document.getElementById('p1-result-all-no').style.display = 'block';
            } else if (getSpecificValue('p1_transporta_mas_de_25kg')) {
                 document.getElementById('p1-result-q5-si').style.display = 'block';
            } else {
                 document.getElementById('p1-result-any-si').style.display = 'block';
            }
        }
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                document.getElementById('p2-result-all-no').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }

    function checkPlanilla2D() {
        const p1 = getPasoValues('p1_');
        if (p1.allAnswered) {
            if (p1.values[0] === false) { // Es NO
                document.getElementById('p1-result-no').style.display = 'block';
            } else { // Es SI
                document.getElementById('p1-result-si').style.display = 'block';
            }
        }
        
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                document.getElementById('p2-result-all-no').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }

    function checkPlanilla2E() {
        const p1 = getPasoValues('p1_');
         if (p1.allAnswered) {
            if (p1.values[0] === false) {
                document.getElementById('p1-result-no').style.display = 'block';
            } else {
                document.getElementById('p1-result-si').style.display = 'block';
            }
        }
        
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                 document.getElementById('p2-result-all-no').style.display = 'block';
            } else if (getSpecificValue('p2_esfuerzo_borg_mayor_7')) {
                document.getElementById('p2-result-q3-si').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }

    function checkPlanilla2F() {
        const p1 = getPasoValues('p1_');
        if (p1.allAnswered) {
            if (p1.values.every(v => v === false)) {
                document.getElementById('p1-result-no').style.display = 'block';
            } else {
                document.getElementById('p1-result-si').style.display = 'block';
            }
        }
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                document.getElementById('p2-result-all-no').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }

    function checkPlanilla2G() {
        // Lógica para Mano-Brazo
        const p1_mb = getPasoValues('p1_mb');
        if (p1_mb.allAnswered) {
             if (p1_mb.values.every(v => v === false)) {
                document.getElementById('p1-mb-result-no').style.display = 'block';
            } else {
                document.getElementById('p1-mb-result-si').style.display = 'block';
            }
        }
        const p2_mb = getPasoValues('p2_mb');
        if (p2_mb.allAnswered) {
            if (p2_mb.values.every(v => v === false)) {
                document.getElementById('p2-mb-result-no').style.display = 'block';
            } else {
                document.getElementById('p2-mb-result-si').style.display = 'block';
            }
        }

        // Lógica para Cuerpo Entero
        const p1_ce = getPasoValues('p1_ce');
        if (p1_ce.allAnswered) {
             if (p1_ce.values.every(v => v === false)) {
                document.getElementById('p1-ce-result-no').style.display = 'block';
            } else {
                document.getElementById('p1-ce-result-si').style.display = 'block';
            }
        }
        const p2_ce = getPasoValues('p2_ce');
        if (p2_ce.allAnswered) {
            if (p2_ce.values.every(v => v === false)) {
                document.getElementById('p2-ce-result-no').style.display = 'block';
            } else {
                document.getElementById('p2-ce-result-si').style.display = 'block';
            }
        }
    }

    function checkPlanilla2H() {
        const p1 = getPasoValues('p1_');
        if (p1.allAnswered) {
            if (p1.values[0] === false) {
                document.getElementById('p1-result-no').style.display = 'block';
            } else {
                document.getElementById('p1-result-si').style.display = 'block';
            }
        }
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values[0] === false) {
                document.getElementById('p2-result-no').style.display = 'block';
            }
        }
    }

    function checkPlanilla2I() {
        const p1 = getPasoValues('p1_');
        if (p1.allAnswered) {
            if (p1.values[0] === false) {
                document.getElementById('p1-result-no').style.display = 'block';
            } else {
                document.getElementById('p1-result-si').style.display = 'block';
            }
        }
        
        const p2 = getPasoValues('p2_');
        if (p2.allAnswered) {
            if (p2.values.every(v => v === false)) {
                document.getElementById('p2-result-all-no').style.display = 'block';
            } else {
                document.getElementById('p2-result-any-si').style.display = 'block';
            }
        }
    }


    // Ejecutar la primera vez al cargar la página
    updateResults(); 

    // Añadir el listener para que se ejecute en cada cambio
    allRadios.forEach(radio => radio.addEventListener('change', updateResults));
});
