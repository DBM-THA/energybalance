<<<<<<< Updated upstream

=======
# envelope.py
from django.db import models
from django.forms import ModelForm, inlineformset_factory
from django.shortcuts import render, redirect
from django.views import View



# ---------------------------------------------------
#  FORMS
# ---------------------------------------------------

class EnvelopeElementForm(ModelForm):
    class Meta:
        model = EnvelopeElement
        fields = ["name", "use_custom_layers", "u_value_external"]


class LayerForm(ModelForm):
    class Meta:
        model = Layer
        fields = ["layer_type", "name", "thickness", "lambda_value", "R_value"]


LayerFormSet = inlineformset_factory(
    EnvelopeElement,
    Layer,
    form=LayerForm,
    extra=3,
    can_delete=True
)


# ---------------------------------------------------
#  VIEW
# ---------------------------------------------------

class EnvelopeCreateView(View):
    template_name = "envelope/envelope_form.html"

    def get(self, request):
        form = EnvelopeElementForm()
        formset = LayerFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request):
        form = EnvelopeElementForm(request.POST)
        formset = LayerFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            element = form.save()
            layers = formset.save(commit=False)

            for layer in layers:
                layer.element = element
                layer.save()

            # U-Wert berechnen
            element.calculate_u_value()

            return redirect("envelope_success")  # muss in urls existieren

        return render(request, self.template_name, {"form": form, "formset": formset})
>>>>>>> Stashed changes
