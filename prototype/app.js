document.addEventListener("DOMContentLoaded", () => {
    console.log("AI Control Center Prototype Loaded");

    const status = {
        cooling: "Normal",
        waterLoop: "Active",
        heatRecovery: "Operating",
        sensors: "Online"
    };

    console.table(status);
});
