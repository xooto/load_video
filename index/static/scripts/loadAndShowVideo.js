$(document).ready(() => {
    $('#capacity').empty()
    var mainMediaSource = new MediaSource
    var metadata
    var mediaSource
    var timeA

    function sourceOpen(e) {
        URL.revokeObjectURL($('#video').attr('src'))
        mediaSource = e.target
        mediaSource.duration = metadata['duration']
        let sourceBuffer = mediaSource.addSourceBuffer(`${metadata['mime_type']}; codecs="${metadata['acodec']}, ${metadata['vcodec']}"`)
        console.log(`${metadata['mime_type']}; codecs="${metadata['acodec']}, ${metadata['vcodec']}"`)
        let isLoading = true

        load()
        timeA = setInterval(function A() {
            if ($('#video').prop("buffered").length > 0) {

                if ($('#video').prop("buffered").end(0) < mediaSource.duration) {

                    if ($('#video').prop("buffered").length > 0 && Math.round($('#video').prop("buffered").end(0)) >= $('#video').prop("currentTime") + 20){

                        if ($('#video').prop("currentTime") >= $('#video').prop("buffered").end(0) - 5 && !isLoading){
                            isLoading = true
                            load()
                        }

                    } else if ($('#video').prop("buffered").length > 0 && $('#video').prop("buffered").end(0) < $('#video').prop("currentTime") + 20 && !isLoading) {
                        isLoading = true
                        load()
                    }

                } else if ($('#video').prop("buffered").end(0) >= mediaSource.duration) {
                    clearInterval(timeA)
                }
            }
        }, 1000)

        function load(){
            fetch ('get/')
            .then (function (response) {
                return response.arrayBuffer()
            })
            .then(function (arrayBuffer){
                if (arrayBuffer.byteLength > 0) {
                    sourceBuffer.appendBuffer(arrayBuffer)
                    isLoading = false
                }
            })
        }
    }

    function B(){
        clearInterval(timeA)
        if (mediaSource) {
            if ($('#video').prop('buffered').length > 0){
                let v = document.querySelector('video[id=video]')
                v.src = ""
                v.load()
            }
        }
    }

    $('#capacity').on("change", () => {
        B()
        if ($('#capacity').val() == "0") {
            return false
        } else {
            $.ajax({
                url: 'video/',
                method: 'post',
                dataType: 'json',
                data: {'csrfmiddlewaretoken': $('input[type=hidden]').val(),
                'res': $('#capacity').val()},
                success: (data) => {
                    B()
                    metadata = data
                    $('#video').attr("src", URL.createObjectURL(mainMediaSource))
                    mainMediaSource.addEventListener('sourceopen', sourceOpen)
                }
            })
        }
    })

    $('#buttonStart').on('click', function () {
        $('#title').text('')
        B()

        $('#capacity').prop('disabled', true)

        $('#capacity').empty()

        if ($('#textRef').val().split("v=")[1].length == 11) {
            $('#buttonStart').prop('disabled', true)
            $.ajax({
                url: 'infoVideo/',
                method: 'post',
                dataType: 'json',
                data: {'csrfmiddlewaretoken': $('input[type=hidden]').val(),
                'textRef': $('#textRef').val()},
                success: (data) => {
                    $('#buttonStart').prop('disabled', false)
                    let capacitys = data['capacitys'].split('/')

                    $('#capacity').append($("<option value='0'>--Качество--</option>"))
                    for (let i = 0; i < capacitys.length - 1; i++) {
                        $('#capacity').append($(`<option value=${capacitys[i]}>${capacitys[i]}</option>`))
                    }

                    $('#title').text(data['title'])

                    $('#capacity').prop('disabled', false)
                },
            })
        } else {
            alert("Ошибка \n\n По какой-то причине возникла ошибка \n Проверьте подключение к интернету \n И проверьте указанную YouTube ссылку")
        }
    })
})