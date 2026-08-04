document.addEventListener("DOMContentLoaded", function(){

    const form = document.querySelector("form");


    form.addEventListener("submit", function(event){

        let allAnswered = true;


        // Check 9 questions
        for(let i = 1; i <= 9; i++){

            let question = document.querySelector(
                'input[name="q' + i + '"]:checked'
            );


            if(!question){

                allAnswered = false;
                break;

            }

        }


        if(!allAnswered){

            event.preventDefault();

            alert("Please answer all the questions before submitting.");

            return;

        }

    });

});