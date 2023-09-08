
const sendAnswer = () => {
    const quizForm = document.querySelector('.quiz-lock');
    const formObj = Object.fromEntries(new FormData(quizForm));
    const urlPath =`${window.location.origin}/answer/`
    fetch(urlPath, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(formObj)
    }).then(res => res.json()).then(data =>{
        if(!data.quiz_pass){
            const rightAnswer = document.querySelector(`#answer_label_${data.right_answer}`);
            if (data.given_answer !== data.right_answer) {
                const wrongAnswer = document.querySelector(`#answer_label_${data.given_answer}`);
                wrongAnswer.style.color = "red";
            }
            rightAnswer.style.color = "green";
            setTimeout(() => {
                document.querySelector('#quiz_body').innerHTML = data.result
            }, 1000)
        }else{
            document.querySelector('#quiz_body').innerHTML = data.result
        }
    })
}