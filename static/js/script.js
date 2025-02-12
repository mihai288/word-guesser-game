document.addEventListener('DOMContentLoaded', function() {
    // Flag-ul care indică dacă toate răspunsurile au fost completate
    let answersComplete = false;

    const checkAnswerBtn = document.getElementById('check-answer-btn');
    const nextLevelBtn = document.getElementById('next-level-btn');

    if (checkAnswerBtn) {
        checkAnswerBtn.addEventListener('click', function() {
            const answerInput = document.getElementById('answer-input');
            const answer = answerInput.value.trim();
            if (answer === "") return; // Nu trimite răspunsuri goale

            fetch('/check_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ answer: answer })
            })
            .then(response => response.json())
            .then(data => {

                if (data.status === 'correct') {
                    const scoreElem = document.getElementById("score");
                    if (scoreElem) {
                        scoreElem.innerText = data.score + ' 💎';
                    }
                    if (typeof data.index !== 'undefined') {
                        const slot = document.getElementById('answer-slot-' + data.index);
                        if (slot) {
                            slot.innerText = data.word;
                            slot.style.border = '2px solid green';
                        }
                    }
                    // Dacă nivelul este complet (toate răspunsurile au fost completate)
                    if (data.complete === true) {
                        answersComplete = true;
                        if (nextLevelBtn) {
                            // Afișăm și activăm butonul
                            nextLevelBtn.style.display = 'block';
                            nextLevelBtn.disabled = false;
                        }
                        answerInput.style.display = 'none';
                    }
                }
                else {
                    answerInput.style.outline = '2px solid red';
                    answerInput.style.boxShadow = '0 0 10px 5px rgba(255, 0, 0, 0.6)';
                    // După 1 secundă, revine la starea normală
                    setTimeout(() => {
                        answerInput.style.outline = 'none';
                        answerInput.style.boxShadow = 'none';
                    }, 1000);
                }
                answerInput.value = "";
            })
            .catch(error => console.error('Error:', error));
        });
    }

    const getAnswerBtn = document.getElementById('get-answer-btn');
    if (getAnswerBtn) {
        getAnswerBtn.addEventListener('click', function() {
            fetch('/get_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {

                if (data.status === 'success' && typeof data.index !== 'undefined') {
                    const slot = document.getElementById('answer-slot-' + data.index);
                    const scoreElem = document.getElementById("score");

                    if (scoreElem) {
                        scoreElem.innerText = data.score + ' 💎';
                    }
                    if (slot) {
                        slot.innerText = data.word;
                        slot.style.border = '2px solid green';
                    }
                    const answerInput = document.getElementById('answer-input');
                    if (data.complete === true) {
                        answersComplete = true;
                        if (nextLevelBtn) {
                            nextLevelBtn.style.display = 'block';
                            nextLevelBtn.disabled = false;
                        }
                        answerInput.style.display = 'none';
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    if (nextLevelBtn) {
        // Dezactivăm butonul până când nivelul este complet
        nextLevelBtn.disabled = true;

        nextLevelBtn.addEventListener('click', function() {
            // Dacă răspunsurile nu sunt complete, ignorăm clicul
            if (!answersComplete) {
                console.log("Completează toate răspunsurile înainte de a trece la nivelul următor.");
                return;
            }

            fetch('/next_level', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Aici poți adăuga logica pentru interceptarea CTRL+R și F5, dacă este necesar
});
