function logout(){

    let confirmLogout = confirm("Are you sure you want to logout?");

    if(confirmLogout){

        window.location.href = "/login/";

    }

}
