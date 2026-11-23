const NOOK = {
  contact: {
    phone: '+852 9288 5723',
    instagram: 'https://www.instagram.com/nookcatcare/'
  },
  pricing: {
    single: 200,
    dailyMultiple: 180,
    twiceDaily: 360,
    islandPerVisit: 10
  }
};

NOOK.contact.tel = 'tel:' + NOOK.contact.phone.replace(/\s/g, '');
NOOK.contact.whatsapp = 'https://wa.me/' + NOOK.contact.tel.replace('tel:+', '');

document.querySelectorAll('[data-contact]').forEach(link => {
  link.href = NOOK.contact[link.dataset.contact];
  if (link.hasAttribute('data-contact-phone')) link.textContent = NOOK.contact.phone;
});

document.querySelectorAll('[data-price]').forEach(label => {
  label.textContent = 'HK$' + NOOK.pricing[label.dataset.price];
});
