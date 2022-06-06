document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);


  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  document.getElementById('emails-load').innerHTML = "";
  document.querySelector('#thead').innerHTML = "";
  document.querySelector('#archive').innerHTML = "";
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelector('#compose-form').onsubmit = () => {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
    
    sendMail(recipients, subject, body);
   
  
  
  return false //prevents from refreshing and going back to main

}
}

function load_mailbox(mailbox) {
  document.getElementById('emails-load').innerHTML = "";//to prevent keep appending each time (duplicates)
  document.querySelector('#archive').innerHTML = "";
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  document.querySelector('#thead').innerHTML = `<tr><th scope="col">From</th><th scope="col">Subject</th><th scope="col">Timestamp</th></tr>`
  getMail(mailbox)
}

function load_mail(email, mailbox) {
  document.getElementById('emails-load').innerHTML = "";//to prevent keep appending each time (duplicates)
  document.querySelector('#thead').innerHTML = "";
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h5>${email.subject}</h5><p>From: ${email.sender}</p><p>To: ${email.recipients}</p><p>Time: ${email.timestamp}</p><hr><p id="mailbody"></p>`;
  document.querySelector('#mailbody').innerText = email.body;//use innerText to parse /n and other markdowns
  

  if (email.archived === true) {
    isarchived = 'Unarchive';
  }
  else {
    isarchived = 'Archive';
  };
  
  if (mailbox != 'sent')
  {
    document.querySelector('#archive').innerHTML = `<button id="reply" class="btn btn-primary">Reply</button> <button id="archivebtn" class="btn btn-danger">${isarchived}</button>`;
    document.querySelector('#archivebtn').addEventListener('click', () => {archiveMail(email), location.reload()});
  }
  if (mailbox === 'sent')
  {
    document.querySelector('#archive').innerHTML = `<button id="reply" class="btn btn-primary">Reply</button>`;
  }
  document.querySelector('#reply').addEventListener('click', () => reply(email));
}

function reply(mail) {
  compose_email();
  document.querySelector('#compose-recipients').value = mail.sender;

  if (mail.subject.substring(0,3) === 'Re:') {
    document.querySelector('#compose-subject').value = mail.subject;
  }
  else {
    document.querySelector('#compose-subject').value = 'Re: ' + mail.subject;
  };
  
  document.querySelector('#compose-body').value = 'On ' + mail.timestamp + ' ' + mail.sender + ' wrote: \n' + mail.body;
}

function getMail(mailbox) {
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);
      emails.forEach(element => {
        // Create new post
        const post = document.createElement('tr');
        if (element.read === true){
          post.style.background = 'gray';
        }
        post.innerHTML = `<td>From: ${element.sender} </td><td>Subject: ${element.subject} </td><td>${element.timestamp}</td>`;
        post.addEventListener('click', function() {
          viewMail(element.id, mailbox)
          console.log('element '+ element.id + ' has been clicked!')
      });
        // Add post to DOM
        document.getElementById('emails-load').append(post);
      });; 
  });
}

function viewMail(id, mailbox) {
  fetch('/emails/' + id)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);
      load_mail(email, mailbox);
      readMail(id)
});
}

function readMail(id) {
  fetch('/emails/' + id, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
}

function archiveMail(email) {
  if (email.archived === false)
  {
     fetch('/emails/' + email.id, {
    method: 'PUT',
    body: JSON.stringify({
      archived: true
    })
  })
  }
  else {
    fetch('/emails/' + email.id, {
      method: 'PUT',
      body: JSON.stringify({
        archived: false
      })
    })
  };
 load_mailbox('inbox')
}

function sendMail(recipients, subject, body) {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .catch(error => {
    console.log('Error:', error);
})
  .then(result => {
      // Print result
      console.log(result);
      if (result.message === "Email sent successfully.")
      {
        load_mailbox('sent');
      }
    else
    {
      document.getElementById('result').innerHTML = result.error;
    }  
  })
  ;
}

