document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
  get_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#read-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#read-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  document.querySelector('#emails-view h3').style.color = '#897D97';
}

function open_email(){

  // Show read email view and hide other views
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#read-view').style.display = 'block';

  const headers = document.querySelectorAll('#read-header p');
  headers.forEach(header => {
    header.innerHTML = '';
  });
}


// Send email
document.addEventListener('DOMContentLoaded', function(){

  document.querySelector('#compose-form').onsubmit = () => {

    // select elements from the form needed for the POST request 
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    const postBody = {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        recipients: recipients, 
        subject: subject, 
        body: body})
    };

    fetch('/emails', postBody)
    .then(response => response.json())
    .then(result => {
      load_mailbox('sent');
      get_mailbox('sent');
    })
    .catch(error => {
      console.log("error: ", error);
    })
    return false;
  };
});

// Get Mailbox 
// Get buttons that will trigger get_mailbox
document.addEventListener('DOMContentLoaded', function(){

  const buttons = document.querySelectorAll('button#inbox, button#sent, button#archived');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      get_mailbox(button.id)});
  });
});


// request emails based on category: inbox/sent/archived
function get_mailbox(mailboxType){

  if (mailboxType === 'archived'){
    mailboxType = mailboxType.slice(0, -1);
  }

  const buildUrl = `emails/${mailboxType}`;
  
  fetch(buildUrl)
  .then(response => response.json())
  .then(emails => {
    if (emails.length === 0)
    {
      const emailsView = document.querySelector('#emails-view');
      const emptyMailbox = document.createElement('h5');
      emptyMailbox.style.color = '#897D97';
      emptyMailbox.innerHTML = 'No emails in this mailbox.'
      emailsView.append(emptyMailbox);
    }else{
      for (let i = 0; i < emails.length; i++){
        addMail(emails[i].sender, emails[i].subject, emails[i].timestamp, emails[i].read, emails[i].id, mailboxType);
      }
    }
  })
  .catch(error => {
    console.log("Error: ", error);
  });
}


// create elements for each email
// display them 
function addMail(sender, title, timestamp, read, emailId, mailType){

  let displayEmailInfo = [sender, title, timestamp];
  const addElement = document.createElement('div');
  const emailsView = document.querySelector('#emails-view');
  addElement.classList.add('email-box');

  // filter background color 
  // based on read/unread
  if (read === true){
    addElement.style.backgroundColor = '#f5f5f5';
  }
  for (let i = 0; i < displayEmailInfo.length; i++){
    
    let addChildElement = document.createElement('p');
    addChildElement.innerHTML = `${displayEmailInfo[i]}`;
    
    addElement.append(addChildElement);
  }

  // set the event listeners for opening an email 
  addElement.addEventListener('click', open_email);

  addElement.addEventListener('click', () => {
    
    // set read property to true 
    const buildUrlUpdate = `emails/${emailId}`;
    const bodyPut = {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    };
    fetch(buildUrlUpdate, bodyPut)
    .then(response => {
      if (response.status == 204)
      {
        console.log(response.status);
      }
    })
    .catch(error => {
      console.log("error: ", error);
    });
    read_email(emailId, mailType);
  });

  emailsView.append(addElement);
}


// Load content for email when clicked 
function read_email(emailId, mail){

  const buildUrlInt = `emails/${emailId}`;

  fetch(buildUrlInt)
  .then(response => response.json())
  .then(email => {
    display_email(email.sender, email.recipients, email.subject, email.timestamp, email.body, email.archived, mail, email.id);
  })
  .catch(error => {
    console.log(error);
  });
}


// helper function to create text elements
function createTextElement(first, last){

  let textElement = document.createElement('p');
  textElement.innerHTML = `${first}: `;
  textElement.style.fontWeight = 'bold';
  textElement.textContent += `${last}`;

  return textElement;
}


// Archive/Unarchive an email
document.addEventListener('DOMContentLoaded', function(){

  const archiveButton = document.querySelector('#archive');

  archiveButton.addEventListener('click', () => {
    let archiveStatus = document.querySelector('#archive').classList.contains('archive');
    let emailId = document.querySelector('#email-id').className;

    let archivePutRequest = {};
    if (archiveStatus === true){
        archivePutRequest = {
        method: 'PUT',
        body: JSON.stringify({
          archived: true
        }),
        headers: {
          'Content-Type': 'application/json'
        }
      };
    }else{
        archivePutRequest = {
        method: 'PUT',
        body: JSON.stringify({
          archived: false
        }),
        headers: {
          'Content-Type': 'application/json'
        }
      };
    }
   
    const buildUrlArch = `emails/${parseInt(emailId)}`;

    fetch(buildUrlArch, archivePutRequest)
    .then(response => {
      if (response.status == 204)
      {
        console.log(response.status);
        load_mailbox('inbox');
        get_mailbox('inbox');
      }
    })
    .catch(error => {
      console.log("error: ", error);
    });
  });
});

function display_email(sender, receiver, subject, timestamp, body, archive, typeOfInbox, displayId){

  const emailHeader = document.querySelector('#read-header');
  const emailBody = document.querySelector('#read-body');
  const archiveButton = document.querySelector('#archive');

  while (emailHeader.firstChild) {
    emailHeader.removeChild(emailHeader.firstChild);
  }
  emailBody.innerHTML = '';

  //add email id to element 
  // retrieve the id when archive/unarchive button is clicked 
  let emailId = document.createElement('p');
  emailId.innerHTML = '';
  emailId.id = 'email-id';
  emailId.removeAttribute('class');
  emailId.classList.add(displayId.toString());
  emailId.style.display = 'None';
  emailHeader.append(emailId);

  let from = createTextElement('From', sender);
  from.id = 'from';
  emailHeader.append(from);

  let to = createTextElement('To', receiver);
  emailHeader.append(to);

  let about = createTextElement('Subject', subject);
  about.id = 'subject';
  emailHeader.append(about);  

  let date = createTextElement('Timestamp', timestamp);
  date.id = 'date';
  emailHeader.append(date);  

  let content = document.createElement('p');
  content.innerHTML = body;
  content.id = 'body';
  emailBody.append(content);

  // display archive button based on type of mailbox
  // set new archive status 
  if (typeOfInbox === 'sent'){
    archiveButton.style.display = 'None';
  }else{
    if (archiveButton.style.display === 'none'){
      archiveButton.style.display = 'inline-block';
    }
    if (archive === false){
      archiveButton.innerHTML = 'Archive';
      if (archiveButton.classList.contains('unarchive'))
      {
        archiveButton.classList.remove('unarchive');
      }
      archiveButton.classList.add('archive');
     
    }else{
      archiveButton.innerHTML = 'Unarchive';
      if (archiveButton.classList.contains('archive'))
      {
        archiveButton.classList.remove('archive');
      }
      archiveButton.classList.add('unarchive');
      
    }
  }
}

// Replay
document.addEventListener('DOMContentLoaded', function(){

  const replyButton = document.querySelector('#reply');

  replyButton.addEventListener('click', () => {

    // retrieve info from prev email 
    // pre-fill info for the create email fields 
    const recepients = document.querySelector('#from');
    const subject = document.querySelector('#subject');
    const timestamp = document.querySelector('#date');

    const sender = recepients.innerHTML.split(":");
    const preFilledTo = sender[sender.length - 1];

    const title = subject.innerHTML.split(":");

    let preFilledSubject;

    if (title[0] === 'Re')
    {
      preFilledSubject = `${title[0]}: ${title[title.length-1].trim()}`
    }else{
      preFilledSubject = `Re: ${title[title.length-1].trim()}`;
    }

    const time = timestamp.innerHTML.split(":");
    const preFilledTime = `${time[time.length-3]}${time[time.length-2]}:${time[time.length-1]}`;

    compose_email();
    document.querySelector('#compose-recipients').value = preFilledTo.trim();
    document.querySelector('#compose-subject').value = preFilledSubject;
    document.querySelector('#compose-body').value = `On ${preFilledTime} ${preFilledTo.trim()} wrote: \n${body.innerHTML}`;
  });
});