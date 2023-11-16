//
//  AnnouncementManager.swift
//  Clew
//
//  Created by Paul Ruvolo on 11/15/21.
//  Copyright © 2021 OccamLab. All rights reserved.
//

import Foundation
import AudioToolbox
import AVFoundation
import UIKit

/// This class manages providing announcements to the user using text to speech.  It will use VoiceOver when
/// that is enabled and the `AVSpeechSynthesizer` otherwise.
class AnnouncementManager: NSObject {
    /// The shared handle to the singleton object of this class
    public static var shared = AnnouncementManager()
    
    /// When VoiceOver is not active, we use AVSpeechSynthesizer for speech feedback
    let synth = AVSpeechSynthesizer()
    
    /// The announcement that is currently being read alogn with whether or not it is preemptable.  If this is nil, that implies nothing is being read
    private var currentAnnouncement: (String, Bool)?
    
    /// The announcement that should be read immediately after this one finishes
    private var nextAnnouncement: (String, Bool)?
    
    /// The private initializer (this should not be called directly)
    private override init() {
        super.init()
        // create listeners to ensure that the isReadingAnnouncement flag is reset properly
        NotificationCenter.default.addObserver(forName: UIApplication.didBecomeActiveNotification, object: nil, queue: nil) { (notification) -> Void in
            self.currentAnnouncement = nil
        }
        
        synth.delegate = self
        NotificationCenter.default.addObserver(forName: UIAccessibility.announcementDidFinishNotification, object: nil, queue: nil) { (notification) -> Void in
            self.currentAnnouncement = nil
            if let nextAnnouncement = self.nextAnnouncement {
                self.nextAnnouncement = nil
                self.announce(announcement: nextAnnouncement.0, isPreemptable: nextAnnouncement.1)
            }
        }
        
        NotificationCenter.default.addObserver(forName: UIAccessibility.voiceOverStatusDidChangeNotification, object: nil, queue: nil) { (notification) -> Void in
            self.currentAnnouncement = nil
        }
    }
    
    /// Communicates a message to the user via speech.  If VoiceOver is active, then VoiceOver is used to communicate the announcement, otherwise we use the AVSpeechEngine
    ///
    /// - Parameter announcement: the text to read to the user
    /// - Parameter isPreemptable: true if we should allow the announcement to be preempted while being spoken
    func announce(announcement: String, isPreemptable: Bool = false) {
        if !Thread.isMainThread {
            DispatchQueue.main.async {
                self.announce(announcement: announcement)
            }
            return
        }
        if let currentAnnouncement = currentAnnouncement {
            if currentAnnouncement.0 == announcement {
                // the announcement is the same, so don't repeat
                return
            }
            // put it on the queue
            nextAnnouncement = (announcement, isPreemptable)
            if !currentAnnouncement.1 {
                // the current anouncement is not preemptable, so wait our turn
                return
            }
            if !UIAccessibility.isVoiceOverRunning {
                // stop the synth.  The notification will advance to the next announcement
                synth.stopSpeaking(at: .immediate)
                return
            } else {
                // remove from the queue since we will speak right away
                nextAnnouncement = nil
            }
            // if voiceover is running, we fall through and let the default code take care of things
        }
        
        if UIAccessibility.isVoiceOverRunning {
            // use the VoiceOver API instead of text to speech
            currentAnnouncement = (announcement, isPreemptable)
            // insert delay to make sure the announcement is properly read.
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                UIAccessibility.post(notification: UIAccessibility.Notification.announcement, argument: announcement)
            }
        } else {
            let audioSession = AVAudioSession.sharedInstance()
            do {
                try audioSession.setCategory(AVAudioSession.Category.playback)
                try audioSession.setActive(true)
                let utterance = AVSpeechUtterance(string: announcement)
                utterance.rate = 0.5
                currentAnnouncement = (announcement, isPreemptable)
                synth.speak(utterance)
            } catch {
                print("Unexpeced error announcing something using AVSpeechEngine!")
            }
        }
    }
}

extension AnnouncementManager: AVSpeechSynthesizerDelegate {
    /// Called when an utterance is finished.  We implement this function so that we can keep track of
    /// whether or not an announcement is currently being read to the user.
    ///
    /// - Parameters:
    ///   - synthesizer: the synthesizer that finished the utterance
    ///   - utterance: the utterance itself
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer,
                           didFinish utterance: AVSpeechUtterance) {
        currentAnnouncement = nil
        if let nextAnnouncement = self.nextAnnouncement {
            self.nextAnnouncement = nil
            announce(announcement: nextAnnouncement.0, isPreemptable: nextAnnouncement.1)
        }
    }
    /// Called when an utterance is canceled.  We implement this function so that we can keep track of
    /// whether or not an announcement is currently being read to the user.
    ///
    /// - Parameters:
    ///   - synthesizer: the synthesizer that finished the utterance
    ///   - utterance: the utterance itself
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer,
                           didCancel utterance: AVSpeechUtterance) {
        currentAnnouncement = nil
        if let nextAnnouncement = self.nextAnnouncement {
            self.nextAnnouncement = nil
            announce(announcement: nextAnnouncement.0, isPreemptable: nextAnnouncement.1)
        }
    }
}
