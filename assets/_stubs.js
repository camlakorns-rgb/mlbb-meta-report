// ---- node DOM shim for template tests ----
var _els = {};
var _elc = 0;
function _mk(id){
  return {
    id: id, innerHTML: '', textContent: '', value: '', className: '', title: '',
    style: {}, dataset: {}, handlers: {}, disabled: false, checked: false, children: [],
    classList: { _s: {}, add: function(c){ this._s[c]=1; }, remove: function(c){ delete this._s[c]; },
                 toggle: function(c,f){ if(f===undefined){ this._s[c]=!this._s[c]; } else { this._s[c]=!!f; } },
                 contains: function(c){ return !!this._s[c]; } },
    addEventListener: function(ev, fn){ (this.handlers[ev] = this.handlers[ev] || []).push(fn); },
    removeEventListener: function(){},
    setAttribute: function(k, v){ this['_at_'+k] = v; },
    getAttribute: function(k){ return this['_at_'+k] !== undefined ? this['_at_'+k] : null; },
    focus: function(){}, blur: function(){},
    click: function(){ var self = this; (this.handlers.click||[]).forEach(function(f){
      f({ target: { closest: function(){ return null; }, getAttribute: function(){ return null; },
                    classList: { contains: function(){ return false; } } }, stopPropagation: function(){} }); }); },
    closest: function(){ return null; },
    appendChild: function(){}, remove: function(){},
    querySelector: function(){ return null; }, querySelectorAll: function(){ return []; }
  };
}
function _el(id){ if(!_els[id]) _els[id] = _mk(id); return _els[id]; }
var document = {
  getElementById: function(id){ return _el(id); },
  createElement: function(tag){ _elc++; return _el('_dyn_'+tag+'_'+_elc); },
  querySelector: function(){ return null; },
  querySelectorAll: function(){ return []; },
  addEventListener: function(){}, removeEventListener: function(){},
  body: _el('body'), documentElement: _el('docEl'), readyState: 'complete'
};
var window = { addEventListener: function(){}, innerWidth: 1280, innerHeight: 900, location: { hash: '' } };
var location = window.location;
