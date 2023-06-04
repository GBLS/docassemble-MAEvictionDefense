$(document).on('daPageLoad', function(){
    var link = document.querySelector("link[rel*='shortcut icon'") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'shortcut icon';
    link.href = "/packagestatic/docassemble.MAEvictionDefense/MADE-favicon.svg?v=2023_06_04";
    document.getElementsByTagName('head')[0].appendChild(link);
});