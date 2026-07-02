document.addEventListener("DOMContentLoaded", () => {
    console.log("AI Control Center Prototype Started");

    const systems = [
        { name: "Cooling System", status: "🟢 Normal" },
        { name: "Water Loop", status: "🟢 Active" },
        { name: "Heat Recovery", status: "🟢 Operating" },
        { name: "Sensor Network", status: "🟢 Online" }
    ];

    systems.forEach(system => {
        console.log(`${system.name}: ${system.status}`);
    });
});
