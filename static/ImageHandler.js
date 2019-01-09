$(document).ready(function() {
    var stamp;
    var groups;
    var viewer;
    var status_skipped;

    function check_status() {
        if (!stamp) {
            // still starting up
            return;
        }
        if (document.hidden) {
            // to reduce complexity, we don't cancel/reschedule the timer
            // when hidden
            status_skipped = true;
            return;
        }
        status_skipped = false;
        $.ajax({
            'dataType': 'json',
            'jsonp': false,  // use CORS
            'success': function(data, status, xhr) {
                if (data.stamp && data.stamp !== stamp) {
                    // retiled existing slides, so reload page
                    document.location.reload();
                }
                if ($('#retiling').is(':visible') !== data.dirty) {
                    // show/hide retiling message
                    if (data.dirty) {
                        $('#retiling').slideDown(200, function() {
                            $(window).resize();
                        });
                    } else {
                        $('#retiling').hide();
                        $(window).resize();
                    }
                }
            },
            'timeout': 60000,
            'url': 'https://openslide-demo.s3.dualstack.us-east-1.amazonaws.com/status.json',
        });
    }
    $(window).on('visibilitychange', function() {
        if (!document.hidden && status_skipped) {
            check_status();
        }
    });
    setInterval(check_status, 300000);

    function populate_images(data, status, xhr) {
        console.log(data);
        stamp = data.stamp;
        groups = data.groups;
        var top = $('<div class="scroll"/>')
        $('#images').removeClass('loading').html('<h1>Slides</h1>').
                    append(top);

        $.each(groups, function(i, group) {
            $('<h2/>').text(group.name).appendTo(top);
            var slides = $('<ul/>');
            top.append(slides);
            $.each(group.slides, function(j, slide) {
                var a = $('<a class="load-image" href="#"/>').attr('title',
                            slide.description).text(slide.name);
                a.data('group', i);
                a.data('slide', j);
                var images = $('<ul class="associated"/>').hide();
                $('<li/>').appendTo(slides).append(a).append(images);
                a.wrap('<div/>');
                $.each(slide.associated, function(k, image) {
                    var a = $('<a class="load-image" href="#"/>').text(
                                image.name);
                    a.data('group', i);
                    a.data('slide', j);
                    a.data('image', k);
                    $('<li/>').appendTo(images).append(a);
                });
            });
        });
        var versions = $('<p id="versions">');
        versions.append('OpenSlide ' + data.openslide +
                    '<br>OpenSlide Python ' + data.openslide_python +
                    '<br>OpenSeadragon ' + OpenSeadragon.version.versionStr);
        top.append(versions);

        $(".load-image").click(function(ev) {
            open_slide($(this));
            ev.preventDefault();
        });

        check_status();
    }

    function open_slide(link) {
        // Load info objects
        var group_id = link.data('group');
        var slide_id = link.data('slide');
        var associated_id = link.data('image');
        var slide = groups[group_id].slides[slide_id];
        var image;
        if (typeof associated_id === 'undefined') {
            image = slide.slide;
        } else {
            image = slide.associated[associated_id];
        }

        // See if we're switching slides
        var prev = $('.current-slide').children('a');
        if (prev.data('group') !== group_id ||
                    prev.data('slide') !== slide_id) {
            // Load properties
            $("#details").html('').addClass('loading');
            $.ajax({
                'dataType': 'json',
                'jsonp': false,  // use CORS
                'success': function(data, status, xhr) {
                    populate_details(slide, data);
                },
                'error': function() {
                    $('#details').removeClass('loading').
                            html("<div class='error'>Couldn't load slide " +
                            "details</div>");
                },
                'url': slide.properties_url
            });

            // Show associated images
            $('.visible-associated').slideUp('fast').
                        removeClass('visible-associated');
            link.parent().siblings('.associated').slideDown('fast').
                        addClass('visible-associated');
        }

        // Create viewer if necessary
        if (!viewer) {
            $("#view").text("");
            viewer = new OpenSeadragon({
                id: "view",
                prefixUrl: "images/",
                animationTime: 0.5,
                blendTime: 0.1,
                constrainDuringPan: true,
                maxZoomPixelRatio: 2,
                minZoomLevel: 1,
                visibilityRatio: 1,
                zoomPerScroll: 2
            });
            viewer.addHandler("open", function() {
                var getTileUrl = viewer.source.getTileUrl;
                viewer.source.getTileUrl = function() {
                    return getTileUrl.apply(this, arguments) + '?v=' + stamp;
                };
                viewer.source.minLevel = 8;
            });
            viewer.scalebar({
                xOffset: 10,
                yOffset: 10,
                barThickness: 3,
                color: '#555555',
                fontColor: '#333333',
                backgroundColor: 'rgba(255, 255, 255, 0.5)',
            });
        }

        // Load slide
        viewer.open(image.source);

        // Update scale
        viewer.scalebar({
            pixelsPerMeter: image.mpp ? (1e6 / image.mpp) : 0,
        });

        // Update selection highlight
        $(".current-slide").removeClass("current-slide");
        link.parent().addClass("current-slide");
    }

    $.ajax({
        'dataType': 'json',
        'jsonp': false,  // use CORS
        'success': populate_images,
        'error': function() {
            $('#images').removeClass('loading').
                    html("<div class='error'>Couldn't load slides</div>");
        },
        'url': 'https://openslide-demo.s3.dualstack.us-east-1.amazonaws.com/info.json'
    });

    // CSS doesn't provide a good way to specify a div of height
    // (100% - height(header))
    $(window).resize(function() {
        $('#content').height($(window).height() -
                    $('#header').outerHeight() - 20);
        $('#view').height($('#viewpane').height() -
                    $('#retiling:visible').outerHeight());
    }).resize();
});