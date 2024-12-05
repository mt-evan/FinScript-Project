for (let i = 1; i <= 3; i++) {
    console.log("Outer loop");
    console.log(i);
    let j = 1;
    while (j <= 3) {
        if (j == 2) {
            console.log("Skipping inner loop");
            console.log(j);
            j = j + 1;
            continue;
        }
        if (i == 3 && j == 3) {
            console.log("Breaking all loops at");
            console.log(i);
            console.log(j);
            break;
        }
        console.log("Inner loop");
        console.log(j);
        console.log("RIGHT HEREEEEE");
        j = j + 1;
    }
}