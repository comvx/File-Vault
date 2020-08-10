// register context-menu-item
Vue.component('context-menu-item', {
  template: '#template-context-menu-item',
  props: {
    icon: ''
  }
});

// register context-menu
Vue.component('context-menu', {
  template: '#template-context-menu',
  props: {
    icon: ''
  },
  methods: {
    newRegister: () => {
      alert('New register');
    },
    remove: () => {
      alert('Remove');
    },
    edit: () => {
      alert('Edit');
    }
  }
});

// start app
var vm = new Vue({
  el: '#app',
  data: {
    contextMenuWidth: null,
    contextMenuHeight: null
  },
  methods: {
    showContextMenu: () => {
      var menu = document.getElementById("context-menu");
      if(!this.contextMenuWidth || !this.contextMenuHeight) {
        menu.style.visibility = "hidden";
        menu.style.display = "block";
        this.contextMenuWidth = menu.offsetWidth;
        this.contextMenuHeight = menu.offsetHeight;
        menu.removeAttribute("style");
      }

      if((this.contextMenuWidth + vm.$event.pageX) >= window.innerWidth) {
        menu.style.left = (vm.$event.pageX - this.contextMenuWidth) + "px";
      } else {
        menu.style.left = vm.$event.pageX + "px";
      }

      if((this.contextMenuHeight + vm.$event.pageY) >= window.innerHeight) {
        menu.style.top = (vm.$event.pageY - this.contextMenuHeight) + "px";
      } else {
        menu.style.top = vm.$event.pageY + "px";
      }
      
      menu.classList.add('active');
    },
    hideContextMenu: () => {
      document.getElementById("context-menu").classList.remove('active');
    }
  }
});