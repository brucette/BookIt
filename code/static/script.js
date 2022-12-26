let month = document.querySelector(".month-year")
if (month) {
  localStorage.setItem('monthYear', month.innerHTML);
} 

let bookingLinks = document.querySelectorAll(".bookingLink")

let times = document.querySelectorAll(".timeslot")

// Add event listener to all days on the calendar view
bookingLinks.forEach((bookingLink) => {
  bookingLink.addEventListener("click",  function() {
    localStorage.setItem('selectedDate', bookingLink.innerHTML);
    console.log('selected:', localStorage.getItem('selectedDate'));
  })
})

// Add event listener to the three different timeslots
times.forEach((time) => {
  time.addEventListener("click",  function() {
    localStorage.setItem('selectedTime', time.innerHTML);
        console.log('selected:', localStorage.getItem('selectedTime'));
    })
})

// Event listener to back button going to the calendar view, for if user goes back to pick a different day
let backToCal = document.getElementById("backToCal")
if (backToCal) {
  backToCal.addEventListener("click", function() {
    localStorage.removeItem('selectedDate');
  })
}

// Event listener to back button going to the timeslosts view, for if user goes back to pick a different time
let backToDay = document.getElementById("backToDay")
if (backToDay) {
  backToDay.addEventListener("click", function() {
    localStorage.removeItem('selectedTime');
  })
}
    
console.log(localStorage.getItem('selectedDate') )
let confirmedDay = localStorage.getItem('selectedDate')
let confirmedmonthYear = localStorage.getItem('monthYear')
let confirmedTime = localStorage.getItem('selectedTime')

document.getElementById("confirmDay").value =  confirmedDay + ' ' + confirmedmonthYear
document.getElementById("confirmTime").value = confirmedTime