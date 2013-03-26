/* From Sky, 3.24.2013 */
document.body.addEventListener('touchmove',function(e){
    if(!$(e.target).hasClass("scrollable")) {
      e.preventDefault();
    }
});