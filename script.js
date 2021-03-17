function toTop() {
    window.scroll({top: 0, left: 0, behavior: 'smooth'});
}

function toAnchor() {
    var input = document.getElementById('inputAnchor').value.toLowerCase().replace(/\s/g, '');
    var anchor = document.getElementById(input);
    if (anchor) {
        anchor.scrollIntoView({behavior: 'smooth'});
    }
    return false;
}