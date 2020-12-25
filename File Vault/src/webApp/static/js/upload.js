Dropzone.options.dropper = {
    paramName: 'file',
    chunking: true,
    forceChunking: true,
    url: '/uploadcontent',
    maxFilesize: 1000, // megabytes
    chunkSize: 100000, // bytes
    init: function() {
        this.on("sending", function(file, xhr, formData) {
          formData.append("destURL", window.location.href);
        });
      }
}