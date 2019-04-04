:github_url: hide
:_comment: The above is a hack backed by our breadcrumbs.html template

{{ fullname | escape | underline }}

.. rubric:: Description

.. automodule:: {{ fullname }}

.. currentmodule:: {{ fullname }}

{% if exceptions %}
.. rubric:: Exceptions

.. autosummary::
   :toctree:
   {% for exc in exceptions %}
   {{ exc }}
   {%- endfor %}
{% endif %}

{% if classes %}
.. rubric:: Classes

.. autosummary::
   :toctree:
   {% for class in classes %}
   {{ class }}
   {%- endfor %}
{% endif %}

{% if functions %}
.. rubric:: Functions

.. autosummary::
   :toctree:
   {% for function in functions %}
   {{ function }}
   {%- endfor %}
{% endif %}
