function previewImage(event, boxId) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const box = document.getElementById(boxId);
      box.style.backgroundImage = `url(${e.target.result})`;
      box.style.border = "none";
      box.querySelector("span").style.display = "none";
    };
    reader.readAsDataURL(file);
  }
}
