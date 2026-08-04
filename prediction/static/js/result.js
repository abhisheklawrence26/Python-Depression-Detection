const ctx = document.getElementById(
    "emotionChart"
);


console.log("Happy:", happy);
console.log("Sad:", sad);
console.log("Neutral:", neutral);
new Chart(ctx, {


    type:"pie",


    data:{


        labels:[

            "Happy",

            "Sad",

            "Neutral"

        ],


        datasets:[

            {

            label:"Emotion Percentage",


            data:[

                happy,

                sad,

                neutral

            ],


            borderWidth:2


            }

        ]


    },


    options:{


        responsive:true,


        plugins:{


            legend:{


                position:"bottom"


            }


        }


    }


});