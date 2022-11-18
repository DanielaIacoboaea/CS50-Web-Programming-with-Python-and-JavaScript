let SubmitButton = document.querySelector(".changing-btn");
const randomWords = ["Curios", "Hungry", "Funny", "Generous", "Stellar", "Trendy", "Grumpy", "Artistic", "Puzzled", "Happy"];
const SubmitButtonLucky = SubmitButton.getAttribute("value");

SubmitButton.addEventListener("mouseenter", () => {
    if (document.querySelector("#main-search").value === "")
    {
        let randomElement = Math.floor(Math.random() * 10);
        let generateAttribute = "I'm Feeling " + randomWords[randomElement];
        SubmitButton.setAttribute("value", generateAttribute);
    }
});

SubmitButton.addEventListener("mouseleave", () => {
    SubmitButton.setAttribute("value", SubmitButtonLucky);
});