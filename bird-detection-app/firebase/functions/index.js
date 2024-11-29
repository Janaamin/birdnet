const {onObjectFinalized} = require("firebase-functions/v2/storage");
const {exec} = require("child_process");
const admin = require("firebase-admin");

admin.initializeApp({
  storageBucket: "robin1234.firebasestorage.app",
});

const storageBucket = admin.storage().bucket();

exports.processAudio = onObjectFinalized(
    {
      bucket: "robin1234.firebasestorage.app",
    },
    async (event) => {
      const object = event.data;
      const bucketName = storageBucket.name;
      const fileName = object.name;

      if (!fileName.endsWith(".wav")) {
        console.log("File is not a .wav file. Skipping processing.");
        return;
      }

      console.log(`Processing file: ${fileName} from bucket: ${bucketName}`);

      try {
        const command =
        `python3 ${__dirname}/process_audio.py ${bucketName} ${fileName}`;
        exec(command, (err, stdout, stderr) => {
          if (err) {
            console.error("Error running process_audio.py:", err);
            return;
          }
          console.log("Audio processed successfully:", stdout);
        });
      } catch (err) {
        console.error("Error processing audio:", err);
      }
    },
);


