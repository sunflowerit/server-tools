odoo.define('profiler.tour', function(require) {
  "use strict";

  var core = require('web.core');
  var tour = require('web_tour.tour');

  var _t = core._t;

  tour.register(
    'profiler_tour',
    {
      url: "/web",
    },
    [
      tour.STEPS.MENU_MORE,
      {
        content: _t("Analyze your application performance in the Profiler app."),
        trigger: '.o_app[data-menu-xmlid="profiler.menu_profiler_root"], .oe_menu_toggler[data-menu-xmlid="profiler.menu_profiler_root"]',
        position: "bottom"
      },
      {
        content: _t("Let's create a new profiler session."),
        trigger: ".o_list_button_add",
        position: "right",
      },
      {
        content: _t("Give this session a name."),
        trigger: "input[name='name']",
        extra_trigger: ".o_form_editable",
        position: "right",
      },
      {
        content: _t("Select a profiling method."),
        trigger: "select[name='python_method']",
        position: "right",
        run: "text Per HTTP request",
      },
      {
        content: _t("When you are happy, save it."),
        trigger: ".o_form_button_save",
        position: "right",
      },
      {
        content: _t("Now enable it to start profiling."),
        trigger: ".o_statusbar_buttons button:containsExact(Enable)",
        extra_trigger: ".o_form_readonly",
        position: "right",
      },
      {
        content: _t("Now disable it to stop profiling."),
        trigger: ".o_statusbar_buttons button:containsExact(Disable)",
        extra_trigger: ".o_form_readonly",
        position: "right",
      },
    ]
  );

});
