

let month = document.querySelector(".month")
if (month) {
  localStorage.setItem('month', month.innerHTML);
} 

let year = document.querySelector(".year")
if (year) {
  localStorage.setItem('year', year.innerHTML);
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

let confirmedDay = localStorage.getItem('selectedDate') //parseInt()
console.log('typeof confirmedDay:', typeof confirmedDay)

let confirmedMonth = localStorage.getItem('month')
console.log('month is:', confirmedMonth)

let confirmedYear = localStorage.getItem('year') //parseInt()
console.log('typeof confirmedYear:', typeof confirmedYear)

let confirmedTime = localStorage.getItem('selectedTime')

function getMonthNumberFromName(monthName) {
  return new Date(`${monthName} 1, 2022`).getMonth();
}

let monthNumber = getMonthNumberFromName(confirmedMonth)
console.log('monthNUM is:', monthNumber)

document.getElementById("confirmDay").value = confirmedDay + '/' + (monthNumber+1).toString() + '/' + confirmedYear
// document.getElementById("confirmDay").value = confirmedDay + ' ' + confirmedMonth + ' ' + confirmedYear
// document.getElementById("confirmDay").value = new Date(confirmedYear, monthNumber, confirmedDay)
document.getElementById("confirmTime").value = confirmedTime