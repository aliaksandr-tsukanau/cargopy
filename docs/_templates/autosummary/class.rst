{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:
   :members:

   ..
      To the end of docstring-based docs
      we add auto-generated summary, kind of ToC for the class:
      an alphabetically sorted table of class members (attributes + methods)

   .. autosummary::
   {% for item in all_attributes + methods %}
      {%- if item not in inherited_members and (item in ['__call__'] or not item.startswith('_')) %}
      {{ item }}
      {%- endif %}
   {%- endfor %}
