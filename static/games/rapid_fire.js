if (!window.RapidFireGame) {

window.RapidFireGame = {

questions: [],
currentQuestion: 0,
score: 0,
correctAnswer: "",
timer: 10,
timerInterval: null,
allowPoints: true,

async start(){

let area = document.getElementById("gameArea")
if(!area) return

let today = new Date().toDateString()
let lastPlayed = localStorage.getItem("rapidFirePlayed")

this.allowPoints = lastPlayed !== today

try{

let res = await fetch("/get-rapid-questions")
let data = await res.json()

this.questions = data.questions || []
this.currentQuestion = 0
this.score = 0

this.loadQuestion()

}catch(err){

area.innerHTML = "<p>Failed to load questions</p>"
console.error(err)

}

},

loadQuestion(){

let area = document.getElementById("gameArea")
if(!area) return

if(this.currentQuestion >= this.questions.length){
this.finishGame()
return
}

let q = this.questions[this.currentQuestion]

this.correctAnswer = q.answer
this.timer = 10

let html = `

<div class="rapid-box">

<div class="rapid-header">

<div>
<i class="fa-solid fa-star" style="color:gold"></i>
${this.score}
</div>

<div>
<i class="fa-solid fa-clock" style="color:red"></i>
<span id="timer">10</span>s
</div>

</div>

<h2 class="rapid-question">${q.question}</h2>

`

q.options.forEach(opt => {

html += `
<button class="rapid-btn option-btn"
onclick="RapidFireGame.submitAnswer('${opt}')">
${opt}
</button>
`

})

html += `<div id="feedback"></div></div>`

area.innerHTML = html

this.startTimer()

},

startTimer(){

clearInterval(this.timerInterval)

this.timerInterval = setInterval(()=>{

this.timer--

let timerElement = document.getElementById("timer")

if(timerElement){
timerElement.innerText = this.timer
}

if(this.timer <= 0){
clearInterval(this.timerInterval)
this.showFeedback(false)
}

},1000)

},

submitAnswer(answer){

clearInterval(this.timerInterval)

if(answer === this.correctAnswer){

if(this.allowPoints){
this.score += 10
}

this.showFeedback(true)

}else{

this.showFeedback(false)

}

},

showFeedback(correct){

let fb = document.getElementById("feedback")
if(!fb) return

if(correct){

fb.innerHTML =
`<i class="fa-solid fa-circle-check" style="color:limegreen"></i> Correct`

}else{

fb.innerHTML =
`<i class="fa-solid fa-circle-xmark" style="color:red"></i> Wrong`

}

this.currentQuestion++

setTimeout(()=>this.loadQuestion(),1200)

},

finishGame(){

let area = document.getElementById("gameArea")
if(!area) return

if(this.allowPoints){

localStorage.setItem("rapidFirePlayed", new Date().toDateString())

fetch("/add-points",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
game:"rapid"
})
})
.then(res=>res.json())
.then(data=>{

if(data.success){

let coinElement = document.getElementById("coinValue")

if(coinElement){
coinElement.innerText = data.coins + " Points"
}

}

})

}

area.innerHTML = `

<div class="rapid-box success-screen">

<h2 class="complete-title">
<i class="fa-solid fa-trophy" style="color:gold"></i>
Quiz Completed!
</h2>

<p class="complete-score">
Score : ${this.score}
</p>

${this.allowPoints ?
`<p class="points-msg">
<i class="fa-solid fa-gem" style="color:#00ffd5"></i>
+20 Coins added!
</p>`
:
`<p class="points-msg">
<i class="fa-solid fa-circle-info" style="color:#ffd166"></i>
Coins already earned today
</p>`
}

<button onclick="RapidFireGame.start()" class="rapid-btn">
Play Again
</button>

</div>
`

}

}

}