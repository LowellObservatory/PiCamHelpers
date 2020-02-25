var han3d = {
    // in ms
    dwell: "150",
    pause: "1000",

    // in minutes
    auto_refresh: "1",

    image_base: "http://localhost/snapshots/anim/",
    basename: "pizini_???.png",
    num_frames: "24",
//    base_starting_number: "0",

    window_size: "div",
    enable_smoothing: "true",

    // NOTE: For background images that are changing on the server, but
    //   have the same filename, you may specify the parameter
    background_static: "n",

    controls: "startstop,speed,step,refresh,looprock,toggle",
    controls_style: "padding:5px; display:flex;",
    controls_tooltip: "Start/Stop, Speed Control, Single Step, Refresh, Rock Forwards/Backwards",

    buttons_style: "flex:auto; margin:2px;",

    toggle_size: "15, 10, 5",
    toggle_colors: "#005914, red, orange",
};
