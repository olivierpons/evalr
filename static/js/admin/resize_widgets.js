/* Olivier Pons / HQF Development */
(function($) {
$(document).ready(function() {
    var mn=30, mx=2000,
        ch=function() {
            var p = $(this).parent().parent().next().find('.resize_dst');
            if (!p.length) {
                p = $(this).parent().parent().parent().find('.resize_dst');
            }
            if (!p.length) return;
            var v=$(this).val();
            if (v<mn) $(this).val(mn);
            if (v>mx) $(this).val(mx);
            if (p && (p.outerHeight()!=v)) p.outerHeight(v);
        };
    $('.resize_src').change(ch).keyup(ch).trigger('change');
});
})(django.jQuery);
